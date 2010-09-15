import logging

from pylons import request, response, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect

from pygitweb.lib.base import BaseController, render
from git.blob import Blob
from stat import S_ISDIR

from os.path import join
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

        c.commits = repo_obj.latest_commits(10)
        c.tags = repo_obj.latest_tags(10)
        c.branches = repo_obj.heads
        c.repo = repo

        return render("repository/summary.tmpl")

    def commit(self):
        repo = request.params.get("repo")
        commitish = request.params.get("commitish")

        if not commitish:
            raise Exception("No commitish specified.")
        if not repo:
            raise Exception("No repo specified.")

        repo_obj = g.repos[repo]

        c.commit = repo_obj.commit(commitish)
        c.formats = g.formats
        c.repo = repo

        return render("repository/commit.tmpl")

    def download(self):
        repo = request.params.get("repo")
        treeish = request.params.get("treeish")
        format = request.params.get("format")

        if not treeish:
            raise Exception("No treeish specified.")
        if not repo:
            raise Exception("No repo specified.")
        if not format:
            raise Exception("No format specified.")

        repo_obj = g.repos[repo]
        treeish = repo_obj.commit(treeish).tree.id

        filename = "pygitweb-%s.%s" % (treeish, format)

        if format == "tar":
            response.content_type = "application/x-tar"
            response.content_disposition = "attachment; filename: %s" % filename
            return repo_obj.archive_tar(treeish)
        elif format == "tar.gz":
            response.content_type = "application/x-gzip"
            response.content_disposition = "attachment; filename=%s" % filename
            return repo_obj.archive_tar_gz(treeish)

        raise Exception("%s not supported" % format)

    def _generate_tree(self, tree_hierarchy, current_path, scratchpad={}):
        if isinstance(tree_hierarchy, git.blob.Blob):
            scratchpad[current_path] = tree_hierarchy
            return

        for child in tree_hierarchy.values():
            self._generate_tree(child, join(current_path, child.name), scratchpad)
        return scratchpad
    def tree(self):
        def has_children(tree_node):
            return len(tree_node.values()) > 0

        repo = request.params.get("repo")
        commitish = request.params.get("commitish")
        path = request.params.get("path", "")

        if not commitish:
            raise Exception("No commitish specified.")
        if not repo:
            raise Exception("No repo specified.")

        repo_obj = g.repos[repo]
        commit_obj = repo_obj.commit(commitish)
        tree_obj = commit_obj.tree

        if path:
            path = path.rstrip('/')
            for folder in path.split('/'):
                tree_obj = tree_obj.get(folder)
            if isinstance(tree_obj, Blob):
                return "BLOB!"

        c.commitish = commitish
        c.tree_obj = tree_obj
        c.path = path
        c.repo = repo

        return render("repository/tree.tmpl")

    def file(self):
        repo = request.params.get("repo")
        commitish = request.params.get("commitish")
        path = request.params.get("path")

        if not repo:
            raise Exception("No repo specified.")
        if not path:
            raise Exception("No path specified.")

        repo_obj = g.repos[repo]
        commit_obj = repo_obj.commit(commitish)
        tree_obj = commit_obj.tree
        for d in path.split("/"):
            if not d:
                continue
            tree_obj = tree_obj[d]

        c.blob = repo_obj.blob(tree_obj.id)
        c.tree = repo_obj.tree(tree_obj.id)
        c.repo = repo
        c.path = path


        return render("repository/file.tmpl")
        #return c.blob.data
