import logging
from os.path import join
import re
import dulwich
from datetime import datetime
from operator import attrgetter
from difflib import unified_diff
import tarfile
from cStringIO import StringIO
from time import time

log = logging.getLogger(__name__)

def compress(repo_obj, id, mode="w:gz"):
    output = StringIO()
    tf = tarfile.open(fileobj=output, mode=mode)
    
    # Get the tree
    obj = repo_obj[id]
    if obj.type == 1:
        obj = repo_obj[obj.tree]
    
    now = time()
    for (path, mode, blob_id) in repo_obj.object_store.iter_tree_contents(obj.id):
        # We need to create the file object
        data = repo_obj[blob_id].data
        file_obj = StringIO(data)
        
        # Create a tarinfo file
        ti = tarfile.TarInfo(path)
        
        # Extract the octal values for the file permissions
        ti.mode = mode & 511
        ti.size = len(data)
        ti.type = tarfile.REGTYPE
        ti.mtime = now
        
        # Add the data with the associated ti info
        tf.addfile(ti, file_obj)
    
    # Close and write it out to the buffer
    tf.close()
    
    # Put the output file pointer back to the beginning
    output.seek(0)
    
    return output


class PyGitRepo(object):
    def __init__(self, repo_path):
        self.repo_obj = dulwich.repo.Repo(repo_path)
        
        # setup the references
        self._parse_refs()
        
        # dulwich has no idea what the owner is; do it separately
        self.owner = self._read_named_file("owner")
        self.description = self._read_named_file("description")

    def _read_named_file(self, path):
        fd = self.repo_obj.get_named_file(path)
        if fd:
            return fd.read().strip()
        return ""

    def _parse_refs(self):
        # Parse out the branches and tags on creation, so that we won't have
        #    to do these on the fly when we want to display them.  This should
        #    get called whenever the refs are updated.
        self.branches = {}
        self.tags = {}
        for ref, sha in self.repo_obj.get_refs().items():
            if ref.startswith('refs/tags/'):
                # Get the commit the tag points at
                self.tags[ref[10:]] = PyGitTag(self.repo_obj[sha])
            elif ref.startswith('refs/heads/'):
                # a head always points at a commit
                self.branches[ref[11:]] = PyGitCommit(self.repo_obj[sha])
            else:
                # We should only ever have heads and tags, but just in case...
                log.warn("Unknown reference: %s (%s)", ref, sha)

    def list_shas(self, head='refs/heads/master', count=50, offset=None):
        already_seen = {}
        array = []
        shas = [self.repo_obj[head]]
        while shas:
            # Sort and grab the last item, the newest
            shas.sort(key=attrgetter('commit_time'))
            sha = shas.pop()
            
            # Skip if we've already visited this sha
            if sha in already_seen:
                continue
    
            # Doesn't matter what this gets set to, as long as the key exists
            already_seen[sha] = None
    
            # If we have an offset, check here
            if not offset or len(already_seen) >= offset:
                array.append(sha)
                
            # If we have enough elements, return them
            if len(array) == count:
                break
            shas.extend([self.repo_obj[s] for s in sha.parents])
            
        return [PyGitCommit(i) for i in array]

    def diffs(self, id_a, id_b=None):
        commit_a = self.repo_obj[id_a]
        if not id_b:
            id_b = commit_a.parents[0]
        commit_b = self.repo_obj[id_b]
        
        if commit_a.commit_time > commit_b.commit_time:
            commit_a, commit_b = commit_b, commit_a
        
        tree_a = commit_a.tree
        tree_b = commit_b.tree
        
        diffs = []
        for ((name_a, name_b), (mode_a, mode_b), (id_a, id_b)) \
                in self.repo_obj.object_store.tree_changes(tree_a, tree_b):
            d = Diff(self.repo_obj, name_a, name_b,
                     id_a, id_b, mode_a, mode_b)
            diffs.append(d)
        return diffs
    
    def archive_tar_gz(self, id):
        return "application/x-gzip", compress(self.repo_obj, id, "w:gz")

    def archive_tar_bz2(self, id):
        return "application/bzip2", compress(self.repo_obj, id, "w:bz2")

    def __getitem__(self, key):
        val = self.repo_obj[key]
        if val.type == 1:
            return PyGitCommit(val)
        return val
    
    def __repr__(self):
        return "<PyGitRepo path='%s'>" % self.repo_obj.path

class Diff(object):
    max_changes = 10
    def __init__(self, repo_obj, name_a, name_b, id_a, id_b, mode_a, mode_b):
        self.new_file = False if name_a else True
        self.deleted = False if name_b else True
        
        self.name_a = name_a or "dev/null"
        self.name_b = name_b or "dev/null"
        self.name = name_a or name_b
        
        self.id_a = id_a
        self.id_b = id_b
        self.id = id_a or id_b
        
        self.mode_a = mode_a
        self.mode_b = mode_b
        
        # Calculate the diffs
        blob_a = repo_obj[id_a].data.splitlines(1) if id_a else ""
        blob_b = repo_obj[id_b].data.splitlines(1) if id_b else ""
        
        self.insertions = 0
        self.deletions = 0
        udiff = [i for i in unified_diff(blob_a, blob_b, join('a', self.name_a), join('b', self.name_b), n=3)]
        for line in udiff[3:]:
            if line[0] == '+':
                self.insertions = self.insertions + 1
            elif line[0] == '-':
                self.deletions = self.deletions + 1
        self.total_changes = self.deletions + self.insertions
        self.diff = "".join(udiff)


class PyGitCommit(object):
    def __init__(self, commit_obj):
        self.commit_obj = commit_obj
        
        # Several fields use this regex
        regex = re.compile(r'^(?P<name>.*) <(?P<email>.*)>$')
        
        # Parse out the author
        author = regex.match(commit_obj.author).groupdict()
        self.author_name = author['name']
        self.author_email = author['email']
        
        # Parse out the committer
        committer = regex.match(commit_obj.committer).groupdict()
        self.committer_name = committer['name']
        self.committer_email = committer['email']
        
        # Timestamps are in unix format; convert them to something readable
        # TODO: We have access to the timezone (author_timezone, etc.), but
        #        this is not used anywhere; should we include it?  By default,
        #        its in GMT.
        self.author_time = datetime.fromtimestamp(commit_obj.author_time)
        self.commit_time = datetime.fromtimestamp(commit_obj.commit_time)
        
        # Split up the summary and the message
        first_nl = commit_obj.message.find('\n')
        self.summary = commit_obj.message[:first_nl].strip()
        self.message = commit_obj.message[first_nl+1:].strip()
        
        self.id = commit_obj.id
        self.tree = commit_obj.tree
        self.parents = commit_obj.parents
        
    def __cmp__(self, obj):
        return cmp(self.commit_obj.commit_time, obj.commit_obj.commit_time)

class PyGitTag(object):
    def __init__(self, tag_obj):
        # Several fields use this regex
        regex = re.compile(r'^(?P<name>.*) <(?P<email>.*)>$')

        # A tag can either be a lightweight tag (literally, a commit), or a
        #    real tag (a reference to a commit, with tag info)
        if tag_obj.type_name == "tag":
            self.tag_time = datetime.fromtimestamp(tag_obj.tag_time) 
            tagger = regex.match(tag_obj.tagger).groupdict()
        else:
            self.tag_time = datetime.fromtimestamp(tag_obj.author_time)
            tagger = regex.match(tag_obj.author).groupdict()

        self.tagger_name = tagger['name']
        self.tagger_email = tagger['email']
        self.id = tag_obj.id

class PyGitDiff(object):
    def __init__(self, blob_a, mode_a, blob_b, mode_b):
        # Get the two trees
        self.mode_a = mode_a
        self.mode_b = mode_b
        self.diff = "".join(unified_diff(
                                blob_a.splitlines(1), blob_b.splitlines(1)))