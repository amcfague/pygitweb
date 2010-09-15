from datetime import date
import pygments
from time import time, mktime, timezone
from operator import itemgetter
from os.path import join

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
    # Convert time_struct to seconds since epoch
    commit_time = mktime(commit_time)

    # The git timestmap uses UTC, so we should to
    seconds = time() + timezone - commit_time

    days = int(round(seconds / 86400))
    if days > 30:
        return date.fromtimestamp(commit_time)
    elif days > 1:
        return "%d days" % days
    elif days == 1:
        return "1 day"

    hours = int(round(seconds / 3600))
    if hours > 1:
        return "%d hours" % hours
    elif hours == 1:
        return "1 hour"

    minutes = int(round(seconds / 60))
    if minutes > 1:
        return "%d minutes" % minutes
    else:
        return "1 minute"

def is_dir(mode):
    from stat import S_ISDIR
    from string import atoi
    return S_ISDIR(atoi(mode, 8))
