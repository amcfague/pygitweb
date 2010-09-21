from datetime import datetime, date
import pygments
from time import time, mktime, timezone
from operator import itemgetter
from os.path import join

PERMISSIONS = {
    "0": "---",
    "1": "--x",
    "2": "-w-",
    "3": "-wx",
    "4": "r--",
    "5": "r-x",
    "6": "rw-",
    "7": "rwx"}

def create_path(*paths):
    join(*[path for path in paths if path])

def highlight_syntax(code):
    lexer = pygments.lexers.guess_lexer(code)
    formatter = pygments.formatters.HtmlFormatter()
    return pygments.highlight(code, lexer, formatter)

def trunc(str, max_length):
    if len(str) < max_length:
        return str

    try:
        index = str.rindex(" ", 0, max_length)
    except ValueError:
        # If we can't find a space, just truncate it mid-word
        index = max_length

    return str[:index] + "..."

def age(commit_time):
    def _round(num):
        return int(round(num))
    
    # Convert and calculate the timedelta
    seconds = time() - mktime(commit_time)

    if seconds < 120:
        return "1 minute"
    if seconds < 3600:
        return "%d minutes" % _round(seconds / 60)
    
    if seconds < 7200:
        return "1 hour"
    if seconds < 86400:
        return "%d hours" % _round(seconds / 3600)
    
    days = seconds / 86400
    if days < 2:
        return "1 day"
    if days < 7:
        return "%d days" % _round(days)
    
    if days < 14:
        return "1 week"
    if days < 56:
        return "%d weeks" % _round(days / 7)
    
    return "%d months" % _round(days / 30)

def is_dir(mode):
    from stat import S_ISDIR
    from string import atoi
    return S_ISDIR(atoi(mode, 8))

def oct_to_sym(str_perms):
    # Chop off all but the rightmost (in case there are more)
    perms = str_perms[-3:]
    
    return "".join(("-",
                   PERMISSIONS[perms[0]],
                   PERMISSIONS[perms[1]],
                   PERMISSIONS[perms[2]]))