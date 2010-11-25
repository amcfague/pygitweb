import logging

from pylons import request, response, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect
from pylons.decorators.cache import beaker_cache

from pygitweb.lib.base import BaseController, render
from git import Blob, Commit
from stat import S_ISDIR
from dulwich.object_store import tree_lookup_path


from os.path import join
log = logging.getLogger(__name__)

class RepositoryController(BaseController):
    def __before__(self, repo=None):
        if not repo:
            response.status_int = 400
            raise Exception("Repository not specified.")

        self.repo_name = repo.rstrip('.git')
                
        if not repo.endswith('.git'):
            repo = repo + ".git"
            
        if repo not in g.repos:
            response.status_int = 404
            raise Exception("Repository `%s' not found" % repo)
        
        self.repo_obj = g.repos[repo]
        c.repo_obj = self.repo_obj
        c.repo = repo

    def summary(self):
        return render("repository/summary.tmpl")
    
    def commit(self, id=None):
        if not id:
            raise Exception("No ID hash specified.")
        
        c.formats = g.formats
        c.commit = self.repo_obj[id]
        c.diffs = self.repo_obj.diffs(id)
        return render("repository/commit.tmpl")

    def download(self, id):
        format = request.params.get('format', g.formats[0])
        if format not in g.formats:
            raise Exception("`%s' format not supported; use %s" % (format, g.formats))
        
        # Generate the filename
        filename = "%s-%s.%s" % (self.repo_name.split('/')[-1], id, format)
        
        # This will display the filename on the browser download dialog
        response.content_disposition = "attachment; filename=%s" % filename
        func_name = "self.repo_obj.archive_%s" % format.replace('.', '_')
        response.content_type, compressed_data = eval(func_name)(id)
        return compressed_data
    
    def tree(self, path=None):
        c.path = path
        c.id = request.params.get('id', 'master')
        
        # Get the path based on the root tree
        perms, id = tree_lookup_path(self.repo_obj.repo_obj.get_object, c.id, c.path)
        obj = self.repo_obj[id]

        # 2 = tree
        # 3 = blob
        if obj.type == 2:
            c.tree_obj = obj
            return render('repository/tree.tmpl')
        else:
            c.blob_obj = obj
            return render('repository/blob.tmpl')
        


    def blob(self, id):
        raise Exception(id)
        c.blob_obj = self.repo_obj[id]
        return render('repository/blob.tmpl')

#class RepositoryController(BaseController):
#    def __before__(self):
#        repo = request.params.get('repo')
#        if not repo.endswith('.git'):
#            repo = repo + ".git"
#        if not repo:
#            response.status_int = 400
#            raise Exception("Repository not specified.")
#        if repo not in g.repos:
#            response.status_int = 404
#            raise Exception("Repositoru `%s' not found" % repo)
#
#        c.repo = repo
#        self.repo_obj = g.repos[repo]
#        c.repo_obj = self.repo_obj
#
#    @beaker_cache(query_args=True)
#    def summary(self):
#        c.commits = self.repo_obj.latest_commits(10)
#        c.tags = self.repo_obj.latest_tags(10)
#        c.branches = self.repo_obj.heads
#
#        return render("repository/summary.tmpl")
#
#    @beaker_cache(query_args=True)
#    def commit(self):
#        commitish = request.params.get("id")
#
#        if not commitish:
#            raise Exception("No commitish specified.")
#
#        c.commit = self.repo_obj.commit(commitish)
#        c.formats = g.formats
#
#        return render("repository/commit.tmpl")
#
#    @beaker_cache(query_args=True)
#    def blob(self):
#        treeish = request.params.get("id")
#        format = request.params.get("format")
#
#        if not treeish:
#            raise Exception("No treeish specified.")
#        if not format:
#            raise Exception("No format specified.")
#
#        treeish = self.repo_obj.commit(treeish).tree.id
#
#        filename = "pygitweb-%s.%s" % (treeish, format)
#
#        if format == "tar":
#            response.content_type = "application/x-tar"
#            response.content_disposition = "attachment; filename: %s" % filename
#            return self.repo_obj.archive_tar(treeish)
#        elif format == "tar.gz":
#            response.content_type = "application/x-gzip"
#            response.content_disposition = "attachment; filename=%s" % filename
#            return self.repo_obj.archive_tar_gz(treeish)
#
#        raise Exception("%s not supported" % format)
#
#    def _generate_tree(self, tree_hierarchy, current_path, scratchpad={}):
#        if isinstance(tree_hierarchy, git.blob.Blob):
#            scratchpad[current_path] = tree_hierarchy
#            return
#
#        for child in tree_hierarchy.values():
#            self._generate_tree(child, join(current_path, child.name), scratchpad)
#        return scratchpad
#
#    @beaker_cache(query_args=True)
#    def tree(self):
#        commitish = request.params.get("id")
#        path = request.params.get("path", "")
#
#        if not commitish:
#            raise Exception("No commitish specified.")
#
#        commit_obj = self.repo_obj.commit(commitish)
#        tree_obj = commit_obj.tree
#
#        if path:
#            path = path.rstrip('/')
#            for folder in path.split('/'):
#                tree_obj = tree_obj.get(folder)
#            if isinstance(tree_obj, Blob):
#                return "BLOB!"
#
#        c.commitish = commitish
#        c.tree_obj = tree_obj
#        c.path = path
#
#        return render("repository/tree.tmpl")
#
#    @beaker_cache(query_args=True)
#    def file(self):
#        commitish = request.params.get("id")
#        path = request.params.get("path")
#
#        if not path:
#            raise Exception("No path specified.")
#
#        commit_obj = self.repo_obj.commit(commitish)
#        tree_obj = commit_obj.tree
#        for d in path.split("/"):
#            if not d:
#                continue
#            tree_obj = tree_obj[d]
#
#        c.blob = self.repo_obj.blob(tree_obj.id)
#        c.tree = self.repo_obj.tree(tree_obj.id)
#        c.path = path
#
#
#        return render("repository/file.tmpl")
#        #return c.blob.data
