import requests
from fsspec import AbstractFileSystem
from fsspec.implementations.memory import MemoryFile


class WandbFS(AbstractFileSystem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import wandb as _wandb
        self.api = _wandb.Api()
        self._wandb = _wandb

    def ls(self, path, detail=False):
        original_path = path
        path = self._strip_protocol(path).rstrip('/').split('/')
        out_files = []
        if len(path) == 1:
            # Only entity was provided
            # We will list all projects
            entity, = path
            for p in self.api.projects(entity):
                out_files.append({
                    'name': f'{entity}/{p.name}',
                    'type': 'directory',
                })
        elif len(path) == 2:
            # Entity and project name were provided
            # We will list all runs
            entity, project = path
            for r in self.api.runs(f'{entity}/{project}'):
                out_files.append({
                    'name': f'{entity}/{project}/{r.id}',
                    'display_name': r.name,
                    'type': 'directory',
                })
        else:
            # We will list files of a single run
            entity, project, run_name, *rest = path
            path = '/'.join(rest)
            base_path = f'{entity}/{project}'
            runs = self.api.runs(base_path, filters={'$or': [{'displayName': run_name}, {'name': run_name}]})
            if runs:
                run = runs[0]
            else:
                raise FileNotFoundError(original_path)

            out_dirs = set()
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

        original_path = path
        entity, project, name, *rest = path.split('/')
        path = '/'.join(rest)
        base_path = f'{entity}/{project}'
        runs = self.api.runs(base_path, filters={'$or': [{'displayName': name}, {'name': name}]})
        if runs:
            run = runs[0]
        else:
            raise FileNotFoundError(original_path)
        try:
            fi = run.file(path)
        except self._wandb.apis.CommError as e:
            # Reraise exception
            if f'does not exist' in e.message:
                raise FileNotFoundError(original_path)
            else:
                raise e

        auth = None if self.api.api_key is None else ('api', self.api.api_key)
        r = requests.get(fi.url, auth=auth)
        if r.status_code == 404:
            raise FileNotFoundError(original_path)
        r.raise_for_status()
        return MemoryFile(None, None, r.content)
