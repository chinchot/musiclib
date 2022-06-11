#!/bin/zsh
rsync app ../musiclib_current/ -r --include="*.py"  --exclude=".DS_Store" --exclude="__pycache__"
rsync . ../musiclib_current/ -r --include-from=deploy.txt --exclude="*"