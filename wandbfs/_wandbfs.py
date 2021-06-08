import requests
from fsspec import AbstractFileSystem
from fsspec.implementations.memory import MemoryFile


class WandbFS(AbstractFileSystem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import wandb as _wandb
        self.api = _wandb.Api()

    def ls(self, path, detail=False):
        path = self._strip_protocol(path).rstrip('/')
        entity, project, run_name, *rest = path.split('/')
        path = '/'.join(rest)
        base_path = f'{entity}/{project}'
        runs = self.api.runs(base_path, filters={'$or': [{'displayName': run_name}, {'name': run_name}]})
        if runs:
            run = runs[0]
        else:
            raise FileNotFoundError(base_path)

        out_dirs = set()
        out_files = []
        base_name = f'{path}/' if path != '' else ''
        for fl in run.files():
            if not fl.name.startswith(base_name):
                continue

            rest_name = fl.name[len(base_name):]
            if '/' in rest_name:
                dirname = rest_name.split('/', 2)[0]
                if dirname not in out_dirs:
                    out_dirs.add(dirname)
                    out_files.append({
                        "name": f'{base_path}/{run_name}/{base_name}{dirname}',
                        "type": "directory",
                    })
            else:
                out_files.append({
                    "name": f'{base_path}/{run_name}/{fl.name}',
                    "type": "file",
                    "size": fl.size,
                    "md5": fl.md5,
                    "mimetype": fl.mimetype,
                })
        if detail:
            return out_files
        else:
            return sorted([f["name"] for f in out_files])

    def _open(
        self,
        path,
        mode="rb",
        block_size=None,
        autocommit=True,
        cache_options=None,
        sha=None,
        **kwargs,
    ):
        if mode != "rb":
            raise NotImplementedError()

        entity, project, name, *rest = path.split('/')
        path = '/'.join(rest)
        base_path = f'{entity}/{project}'

        # Load weights from runs
        runs = self.api.runs(base_path, filters={'$or': [{'displayName': name}, {'name': name}]})
        if runs:
            run = runs[0]
        # model_name = run.config['model']
        fi = run.file(path)
        auth = None if self.api.api_key is None else ('api', self.api.api_key)
        r = requests.get(fi.url, auth=auth)
        if r.status_code == 404:
            raise FileNotFoundError(path)
        r.raise_for_status()
        return MemoryFile(None, None, r.content)
