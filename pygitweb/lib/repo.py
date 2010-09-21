import logging
from git import Repo, Commit, Tag
from os.path import join
from time import asctime

log = logging.getLogger(__name__)

class PyGitRepo(object):
    def __init__(self, repo_path):
        self.repo_obj = Repo(repo_path)
        self.branches = [PyGitHead(branch) for branch in self.repo_obj.branches] 

    def latest_commits(self, count=10):
        try:
            # Get the lastest COUNT commits
            commits = self.repo_obj.git.rev_list(
                    all=True, max_count=count, date_order=True).split('\n')
        except Exception as exc:
            # If we fail, log it and return an empty list
            log.exception(exc)
            return []
        
        # Create commits
        return [self.commit(commit) for commit in commits]
        return [PyGitCommit(Commit(self.repo_obj, commit)) for commit in commits]

    def latest_tags(self, count=10):
        try:
            # Get the latest COUNT tags
            tags = self.repo_obj.git.rev_list(tags=True, max_count=count,
                            no_walk=True, date_order=True).split('\n')
        except Exception as exc:
            log.exception(exc)
            return []
        
        return [PyGitTag(self.repo_obj, Tag(self.repo_obj.git.describe(tag), tag)) for tag in tags]

    def commit(self, id):
        # Get the commit object
        commit_obj = self.repo_obj.commit(id)
        
        # Generate the tags
        tags = {}
        for tag in self.repo_obj.tags:
            if tag.commit.id == id:
                tags[tag.commit.id] = PyGitTag(self.repo_obj, tag)
        
        # Generate the heads
        heads = [head for head in self.repo_obj.heads if head.commit.id == id]
        
        # Return a generated commit
        return PyGitCommit(commit_obj, tags=tags, heads=heads)

    def tree(self, id):
        # Get the tree object
        tree_obj = self.repo_obj.tree(id)
        return PyGitTree(tree_obj)

    def blob(self, id):
        # Get the blob object
        blob_obj = Blob(self.repo_obj, id)
        return PyGitBlob(blob_obj)

    def __repr__(self):
        return "<PyGitRepo path='%s'>" % self.repo_obj.path

class PyGitCommit(object):
    def __init__(self, commit_obj, tags={}, heads={}):
        self.commit_obj = commit_obj
        self.tags = tags
        self.heads = heads
        
    @property
    def author_name(self):
        return self.commit_obj.author.name
    @property
    def author_email(self):
        return self.commit_obj.author.email
    @property
    def authored_date(self):
        return self.commit_obj.authored_date
    @property
    def committer_name(self):
        return self.commit_obj.committer.name
    @property
    def committer_email(self):
        return self.commit_obj.committer.email
    @property
    def commit_date(self):
        return self.commit_obj.committed_date
    @property
    def summary(self):
        return self.commit_obj.summary
    @property
    def message(self):
        return self.commit_obj.message
    @property
    def deletions(self):
        return self.commit_obj.stats.total['deletions']
    @property
    def insertions(self):
        return self.commit_obj.stats.total['insertions']
    @property
    def files_changed(self):
        return self.commit_obj.stats.total['files']
    @property
    def id(self):
        return self.commit_obj.id
    @property
    def tree(self):
        return PyGitTree(self.commit_obj.tree)
    @property
    def parents(self):
        return [PyGitCommit(parent) for parent in self.commit_obj.parents]
    @property
    def diffs(self):
        return [PyGitDiff(diff, self.commit_obj.stats) for diff in self.commit_obj.diffs]
    @property
    def mode(self):
        return self.commit_obj.mode
    
    def __repr__(self):
        return str("<PyGitCommit id='%s'>" % self.commit_obj.id)

class PyGitDiff(object):
    def __init__(self, diff_obj, stats_obj):
        self.diff_obj = diff_obj
        self.stats_obj = stats_obj
    
    @property
    def a_commit(self):
        return self.diff_obj.a_commit
    @property
    def a_mode(self):
        return self.diff_obj.a_mode
    @property
    def a_path(self):
        return self.diff_obj.a_path
    @property
    def b_commit(self):
        return self.diff_obj.b_commit
    @property
    def b_mode(self):
        return self.diff_obj.b_mode
    @property
    def b_path(self):
        return self.diff_obj.b_path
    @property
    def deleted_file(self):
        return self.diff_obj.deleted_file
    @property
    def diff(self):
        return self.diff_obj.diff
    @property
    def new_file(self):
        return self.diff_obj.new_file
    @property
    def rename_from(self):
        return self.diff_obj.rename_from
    @property
    def rename_to(self):
        return self.diff_obj.rename_to
    @property
    def renamed(self):
        return self.diff_obj.renamed
    @property
    def deletions(self):
        return self.stats_obj.files[self.b_path]["deletions"]
    @property
    def insertions(self):
        return self.stats_obj.files[self.b_path]["insertions"]
    @property
    def lines(self):
        return self.stats_obj.files[self.b_path]["lines"]
    @property
    def total_lines(self):
        print self.diff_obj.a_commit
        print self.diff_obj.a_mode
        print self.diff_obj.a_path
        print self.diff_obj.b_commit
        print self.diff_obj.b_mode
        print self.diff_obj.b_path
        print dir(self.diff_obj.b_commit)

class PyGitTree(object):
    def __init__(self, tree_obj):
        self.tree_obj = tree_obj
    
    @property
    def get(self, key):
        return self.tree_obj.get(key)
    @property
    def items(self):
        return self.tree_obj.items()
    @property
    def keys(self):
        return self.tree_obj.keys()
    @property
    def values(self):
        return self.tree_obj.values()
    @property
    def id(self):
        return self.tree_obj.id

class PyGitBlob(object):
    pass

class PyGitHead(object):
    def __init__(self, head_obj):
        self.head_obj = head_obj
        self.commit_obj = PyGitCommit(head_obj.commit)
    
    @property
    def name(self):
        return self.head_obj.name
    
    @property
    def commit(self):
        return self.commit_obj
    
    def __repr__(self):
        return str("<PyGitHead id='%s'>" % self.head_obj.name)

class PyGitTag(object):
    def __init__(self, repo_obj, tag_obj):
        self.tag_obj = tag_obj

        # The commit in the tag is just a hash--not a commit object
        self.commit_obj = PyGitCommit(Commit(repo_obj, tag_obj.commit))
    
    @property
    def name(self):
        return self.tag_obj.name
    @property
    def commit(self):
        return self.commit_obj