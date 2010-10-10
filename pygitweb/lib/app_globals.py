"""The application's Globals object"""

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from pylons import config
import os
from git.utils import is_git_dir
from pygitweb.lib.repo import PyGitRepo
import logging

log = logging.getLogger(__name__)


def find_repositories(repo_root):
    repos = {}
    for dirpath, dirnames, dirfiles in os.walk(repo_root, topdown=True):
        # Loop through a copy of the list, so we can remove directories out
        #    from under the iteration.  Once we parse a name.git directory,
        #    we don't want to parse the things underneath.
        for dir in dirnames[:]:
            # Generate the absolute path for the git directory
            absolute_path = os.path.join(dirpath, dir)

            # Ignore non-bare repos
            if dir == ".git" or os.path.exists(os.path.join(dir, '.git')):
                log.warn("Not a bare repository; skipping: %s", absolute_path)
                dirnames.remove(dir)
                continue

            # Check to see if this directory is a git repository
            if not is_git_dir(absolute_path):
                continue
            
            # Generate the absolute and relative paths
            relative_path = os.path.relpath(absolute_path, repo_root)
            repos[relative_path] = PyGitRepo(absolute_path)
            log.info("Bare git repository added: %s" % absolute_path)
            dirnames.remove(dir)

    return repos

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application

    """

    def __init__(self, config):
        """One instance of Globals is created during application
        initialization and is available during requests via the
        'app_globals' variable

        """
        self.cache = CacheManager(**parse_cache_config_options(config))
        self.repos = find_repositories(config.get('git_repos'))
        self.formats = config.get("formats", "tar.gz,tar.bz2,zip").split(",")
        self.formats.sort()
        
        log.info("Supporting the following formats: %s" % ", ".join(self.formats))