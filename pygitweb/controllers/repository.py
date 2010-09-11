import logging

from pylons import request, response, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect

from pygitweb.lib.base import BaseController, render

log = logging.getLogger(__name__)

class RepositoryController(BaseController):

    def summary(self):
        repo = request.params.get("repo")
        if not repo:
            response.status_int = 400
            return "Repository not specified."

        if not repo.endswith(".git"):
            repo = repo + ".git"

        if repo not in g.repos:
            response.status_int = 404
            return "Repository `%s' not found" % repo

        repo_obj = g.repos[repo]

        return [i.name + "<br>\n" for i in repo_obj.latest_commits(10)]
