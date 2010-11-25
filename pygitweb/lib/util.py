from datetime import datetime, date
import pygments
from time import time, mktime, timezone
from operator import itemgetter
from os.path import join
import string
from stat import S_ISDIR

PERMISSIONS = {
    "0": "---",
    "1": "--x",
    "2": "-w-",
    "3": "-wx",
    "4": "r--",
    "5": "r-x",
    "6": "rw-",
    "7": "rwx"}

TYPES = {
    "000":'-',
    "400":'!',
    "040":'d',
    "010":'-',
    "120":'l',
    "160":'m'}

def create_path(*paths):
    join(*[path for path in paths if path])

def highlight_diff(diff):
    lexer = pygments.lexers.DiffLexer()
    formatter = pygments.formatters.HtmlFormatter()
    return pygments.highlight(diff, lexer, formatter)

def highlight_blob(blob):
    def get_lexer():
        try: return pygments.lexers.get_lexer_for_mimetype(blob.mime_type)
        except pygments.util.ClassNotFound: pass
        
        try: return pygments.lexers.get_lexer_for_filename(blob.name)
        except pygments.util.ClassNotFound: pass
        
        try: return pygments.lexers.guess_lexer(blob.data)
        except pygments.util.ClassNotFound: pass
        
        return pygments.lexers.TextLexer()

    lexer = get_lexer()
    formatter = pygments.formatters.HtmlFormatter(linenos=True)
    return pygments.highlight(blob.data, lexer, formatter)

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
    delta = datetime.today() - commit_time
    
    seconds = (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10**6) / 10**6
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

def trim_first_line(msg):
    pos = string.find(msg, '\n')
    if pos == -1:
        return ""
    return msg[pos+1:]

def oct_to_sym(str_perms):
    if not isinstance(str_perms, str):
        str_perms = oct(str_perms)
    
    perms = str_perms[-3:]
    type = str_perms[:3]
    
    return "".join((TYPES[type],
                   PERMISSIONS[perms[0]],
                   PERMISSIONS[perms[1]],
                   PERMISSIONS[perms[2]]))

def count_lines(msg):
    return string.count(msg, '\n')

text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
_null_trans = string.maketrans("", "")
def istext(s):
    if "\0" in s:
        return False
    
    if not s:  # Empty files are considered text
        return True

    # Only use the first 1024 (1KB)--we're not sure how big the file is, and we
    #    don't want to read a massive file into memory for this.
    s = s[:1024]

    # Get the non-text characters (maps a character to itself then
    # use the 'remove' option to get rid of the text characters.)
    t = s.translate(_null_trans, text_characters)

    # If more than 30% non-text characters, then
    # this is considered a binary file
    return len(t)/len(s) < 0.30


FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
def hex_dump(src, length=8):
    i = 0
    result = ''
    while src:
       s, src = src[:length], src[length:]
       hexa = ' '.join(["%02X" % ord(x) for x in s])
       s = s.translate(FILTER)
       result += "%04X   %-*s   %s\n" % (i, length*3, hexa, s)
       i+=length

    return result