#!/usr/bin/env python3

import json
import subprocess
import sys
import os

import click

@click.command()
@click.option("--add", help="add instead of update subtree(s)", is_flag=True)
@click.option("--chdir", help="cd to dir first", type=str)
@click.argument("repos", nargs=-1, type=click.STRING)
def main(add, repos, chdir):
    to_update = set(repos)
    print(add, repos, chdir, to_update)

    if chdir is not None:
        os.chdir(chdir)

    with open("subtrees.json", "r") as f:
        subtrees = json.load(f)

    if add:
        mode = "add"
    else:
        mode = "pull"

    for entry in subtrees:
        path = entry["path"]
        url = entry["url"]
        branch = entry["branch"]

        if len(to_update) == 0 or path in to_update or url in to_update:
            try:
                subprocess.check_call(["git", "subtree", mode, "-m", "updated %s" % path, "-P", path, url, branch])
            except subprocess.CalledProcessError:
                print("%sing %s failed" % (mode, path))

if __name__=="__main__":
    main()
