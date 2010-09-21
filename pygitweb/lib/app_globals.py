"""The application's Globals object"""

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from pylons import config
import os
from git.utils import is_git_dir
from pygitweb.lib.repo import PyGitRepo

def find_repositories(repo_root):
    repos = {}
    for dirpath, dirnames, dirfiles in os.walk(repo_root):
        for dir in dirnames:
            # Generate the absolute path for the git directory
            absolute_path = os.path.join(dirpath, dir)

            # Check to see if this directory is a git repository
            if not is_git_dir(absolute_path):
                continue

            # Generate the absolute and relative paths
            relative_path = os.path.relpath(absolute_path, repo_root)
            repos[relative_path] = PyGitRepo(absolute_path)

            # Since this is a .git dir, we don't need to look any further;
            #   remove it from the list of directories to walk
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
