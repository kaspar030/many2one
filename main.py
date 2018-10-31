import json
import os
import subprocess
import sys

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

from log import log

from shlex import quote


class GithubWebhookHandler(tornado.web.RequestHandler):
    def initialize(self, repo_dirs):
        self.repo_dirs = repo_dirs

    def post(self):
        hook_type = self.request.headers.get('X-Github-Event')

        if hook_type == "push":
            data = json.loads(self.request.body.decode("utf-8"))
            try:
                repo = data["repository"]["ssh_url"]
                commit = data["head_commit"]["id"]
                handle_notification(self.repo_dirs, repo, commit)
                self.write("ok")
            except:
                log.info(json.dumps(data, sort_keys=False, indent=4))

        else:
            log.warning("unhandled github event: %s", hook_type)
            self.write("error")


class NotifyHandler(tornado.web.RequestHandler):
    def initialize(self, repo_dirs):
        self.repo_dirs = repo_dirs

    def post(self):
        data = json.loads(self.request.body)
        repo = data["repo"]
        commit = data.get("commit")
        handle_notification(self.repo_dirs, repo, commit)


class Webserver(object):
    def __init__(self, port, repo_dirs):
        self.secret = "__secret"
        self.port = port
        self.application = tornado.web.Application([
            (r"/github", GithubWebhookHandler, dict(repo_dirs=repo_dirs)),
            (r"/notify", NotifyHandler, dict(repo_dirs=repo_dirs)),
                ])
        self.server = tornado.httpserver.HTTPServer(self.application)
        self.server.listen(self.port)

    def run(self):
        log.info("many2one started")
        tornado.ioloop.IOLoop.instance().start()


def handle_notification(repo_dirs, repo, commit=None):
    log.info("got notification for repo %s, commit %s", repo, commit)

    for repo_dir in repo_dirs:
        try:
            log.info("updating %s in %s", repo, repo_dir)
            subprocess.check_call(["./update-subtrees.py", "--chdir", repo_dir, quote(repo)])
            subprocess.check_call(["git", "-C", repo_dir, "push"])
        except subprocess.CalledProcessError:
            log.error("updating %s in %s failed", repo, repo_dir)


def main():
    repo_dirs = sys.argv[1:]
    w = Webserver(8080, repo_dirs)

    w.run()

if __name__=="__main__":
    main()
