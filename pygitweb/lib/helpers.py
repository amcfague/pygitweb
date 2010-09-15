"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password
from time import mktime, asctime
from pylons import url
from webhelpers.html.tags import link_to, stylesheet_link
from webhelpers.html.tools import mail_to

from pygitweb.lib.util import age, highlight_syntax, trunc, is_dir
from os.path import join
