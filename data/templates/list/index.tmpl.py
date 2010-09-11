# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1284087707.1799779
_template_filename='/Users/amcfague/Documents/src/pygitweb/pygitweb/templates/list/index.tmpl'
_template_uri='list/index.tmpl'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<table border="1">\n    <thead>\n        <tr>\n            <th>Name</th>\n            <th>Description</th>\n            <th>Owner</th>\n            <th>Last Change</th>\n            <th>&nbsp;</th>\n        </tr>\n    </thead>\n    <tbody>\n')
        # SOURCE LINE 12
        for (repo_name, repo_obj) in c.repos.items():
            # SOURCE LINE 13
            __M_writer(u'        <tr>\n            <td>')
            # SOURCE LINE 14
            __M_writer(escape(repo_name))
            __M_writer(u'</td>\n            <td>')
            # SOURCE LINE 15
            __M_writer(escape(repo_obj.description))
            __M_writer(u'</td>\n            <td>')
            # SOURCE LINE 16
            __M_writer(escape(repo_obj.owner))
            __M_writer(u'</td>\n            <td>')
            # SOURCE LINE 17
            __M_writer(escape(repo_obj.last_change))
            __M_writer(u'</td>\n            <td>shortlog</td>\n        </tr>\n')
            pass
        # SOURCE LINE 21
        __M_writer(u'    </tbody>\n</table>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


