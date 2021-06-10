# Wandb fsspec implementation
[Wandb](https://docs.wandb.ai/) is a machine learning tool which allows you to tracks your experiments. While the experiment is running, it tracks its metrics and helps you visualize the progress. You can also upload files such as configuration files, models, datasets (some files are uploaded automatically). After the experiment is finished, you can access the experiment's files (only read-only). This implementation allows researchers who use wandb to access the finished experiment's files using the [fsspec interface](https://github.com/intake/filesystem_spec).

## Getting started
Install the package by running:
```
pip install wandbfs
```

Then, you can open any file from your wandb runs as follows:
```
import fsspec

f = fsspec.open('wandb://{entity}/{project}/{run_name_or_run_id}/{path}')
```

You can also list the files and subdirectories by using the `ls` command.

```
import fsspec

fs = fsspec.filesystem('wandb')

files = fs.ls('{entity}/{project}/{run_name_or_run_id}/{path}')
```

Alternatively, you can list projects or runs:
```
import fsspec

fs = fsspec.filesystem('wandb')

projects = fs.ls('{entity}')
runs = fs.ls('{entity}/{project}')
```
