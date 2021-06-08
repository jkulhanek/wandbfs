# Wandb fsspec implementation
This repository implements the wandb fsspec protocol.

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
