import git
import logging
from os.path import join
log = logging.getLogger(__name__)
from time import asctime

class GitRepo(git.repo.Repo):
    def __init__(self, *args, **kwargs):
        super(GitRepo, self).__init__(*args, **kwargs)

    def latest_commits(self, count=1):
        newest_commits = self.git.rev_list(
                        all=True, max_count=count, date_order=True).split('\n')

        if not newest_commits:
            raise Exception("No commits found")

        return [git.commit.Commit(self, commit) for commit in newest_commits]

    def latest_tags(self, count=1):
        try:
            newest_tags = self.git.rev_list(no_walk=True, tags=True,
                                    max_count=count, date_order=True).split('\n')
        except:
            return []

        return [git.tag.Tag(self.git.describe(tag), tag)
                for tag in newest_tags]

    @property
    def last_change(self):
        return asctime(self.latest_commits(count=1)[0].committed_date)

    @property
    def owner(self):
        filename = join(self.git.git_dir, 'owner')
        try:
            return file(filename).read().rstrip()
        except IOError:
            return ""

    def archive(self, format, treeish='master', prefix=None, **kwargs):
        from cStringIO import StringIO
        ios = StringIO()
        if treeish is None:
            treeish = self.active_branch
        if prefix and 'prefix' not in kwargs:
            kwargs['prefix'] = prefix
        kwargs['output_stream'] = ios

        self.git.archive(treeish, **kwargs)
        return ios

    def archive_tar_bz2(self, *args, **kwargs):
        return self.archive(format="tar.bz2", *args, **kwargs)
    def archive_zip(self, *args, **kwargs):
        return self.archive(format="zip", *args, **kwargs)
