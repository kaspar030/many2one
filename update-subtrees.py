#!/usr/bin/env python3

import json
import subprocess
import sys
import os

import click

@click.command()
@click.option("--chdir", help="cd to dir first", type=str)
@click.argument("repos", nargs=-1, type=click.STRING)
def main(repos, chdir):
    to_update = set(repos)

    if chdir is not None:
        os.chdir(chdir)

    with open("subtrees.json", "r") as f:
        subtrees = json.load(f)

    print(subtrees)
    for entry in subtrees:
        path = entry["path"]
        url = entry["url"]
        branch = entry["branch"]

        if len(to_update) == 0 or path in to_update or url in to_update:
            if not os.path.isdir(path):
                mode = "add"
            else:
                mode = "pull"

            try:
                subprocess.check_call(["git", "subtree", mode, "-m", "updated %s" % path, "-P", path, url, branch])
            except subprocess.CalledProcessError:
                print("%sing %s failed" % (mode, path))

if __name__=="__main__":
    main()
