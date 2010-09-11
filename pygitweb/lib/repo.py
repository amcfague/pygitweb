import git
import logging
from os.path import join
log = logging.getLogger(__name__)
from time import asctime

class GitRepo(git.repo.Repo):
    def __init__(self, *args, **kwargs):
        super(GitRepo, self).__init__(*args, **kwargs)

    def latest_commits(self, count=1, sort="-committerdate"):
        newest_head = git.head.Head.find_all(self, count=count, sort=sort)
        if newest_head:
            return newest_head
        raise Exception("No head found")

    @property
    def last_change(self):
        return asctime(self.latest_commits(count=1)[0].commit.committed_date)

    @property
    def owner(self):
        filename = join(self.git.git_dir, 'owner')
        try:
            return file(filename).read().rstrip()
        except IOError:
            return ""
