# Copyright Bors LTD
# This file is part of django-icons-mimetypes.
#
#    django-icons-mimetypes is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Django-icons-mimetypes is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with django-icons-mimetypes.  If not, see <http://www.gnu.org/licenses/>.

from urllib.parse import urljoin

from django import template
from django.template.base import Node
from django.templatetags.static import PrefixNode

from .. import icons


register = template.Library()


class MimetypesIconNode(Node):

    def __init__(self, mimetype, size, varname=None):
        self.mimetype = mimetype
        self.size = size
        self.varname = varname

    def url(self, context):
        mimetype = self.mimetype.resolve(context)
        size = self.size.resolve(context)
        return icons.get_icon(mimetype, size=size)

    def render(self, context):
        url = self.url(context)
        if self.varname is None:
            return url
        context[self.varname] = url
        return ''

    @classmethod
    def handle_simple(cls, mimetype, size=icons.SIZE_DEFAULT):
        path = icons.get_icon(mimetype, size=size)
        return urljoin(PrefixNode.handle_simple("STATIC_URL"), path)

    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse prefix node and return a Node.
        """
        bits = token.split_contents()
        tagname = bits.pop(0)

        if not bits:
            raise template.TemplateSyntaxError(
                "'%s' takes at least one argument (path to file)" % (tagname,))

        mimetype = parser.compile_filter(bits.pop(0))

        if bits and bits[0] != 'as':
            size = parser.compile_filter(bits.pop(0))
        else:
            size = template.Variable('"%s"' % (icons.SIZE_DEFAULT,))

        if bits and bits[0] == 'as':
            try:
                varname = bits[1]
            except IndexError:
                raise template.TemplateSyntaxError(
                    "'%s as' takes one argument (varname)" % (tagname,))
        else:
            varname = None

        return cls(mimetype, size, varname)


@register.tag('icon')
def do_icon(parser, token):
    """
    A template tag that returns the URL to a mimetype icon
    using staticfiles' storage backend

    Usage::

        {% icon mimetype [size] [as varname] %}

    Examples::

        {% icon "image/jpeg" %}
        {% icon "image/jpeg" "32x32" %}
        {% icon "image/jpeg" size %}
        {% icon mimetype %}
        {% icon mimetype "16x16" %}
        {% icon mimetype size %}
        {% icon "application/pdf" as pdf_icon %}
        {% icon "application/pdf" "48x48" as pdf_icon %}
        {% icon "application/pdf" size as pdf_icon %}
        {% icon mimetype as pdf_icon %}
        {% icon mimetype "32x32" as pdf_icon %}
        {% icon mimetype size as pdf_icon %}

    """
    return MimetypesIconNode.handle_token(parser, token)


def icon(mimetype, size=icons.SIZE_DEFAULT):
    return MimetypesIconNode.handle_simple(mimetype, size=size)
