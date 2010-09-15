import logging

from pylons import request, response, session, tmpl_context as c, url, config
from pylons.controllers.util import abort, redirect

from pygitweb.lib.base import BaseController, render

from time import asctime
from pylons import app_globals as g
import os

log = logging.getLogger(__name__)

class ListController(BaseController):
    def index(self):
        c.repos = g.repos
        return render("list/index.tmpl")
