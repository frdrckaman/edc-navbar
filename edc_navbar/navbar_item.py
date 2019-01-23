import copy

from django.conf import settings
from django.template.loader import render_to_string
from django.urls.base import reverse


class NavbarItemError(Exception):
    pass


class NavbarItem:

    """A class that represents a single item on a navbar.
    """

    template_name = f'edc_navbar/bootstrap{settings.EDC_BOOTSTRAP}/navbar_item.html'

    def __init__(self, name=None, title=None,
                 label=None, alt=None, url_name=None, html_id=None,
                 glyphicon=None, fa_icon=None, icon=None,
                 icon_width=None, icon_height=None, no_url_namespace=None,
                 active=None, permission_codename=None):
        self.alt = alt or label or name
        self.name = name
        if no_url_namespace:
            self.url_name = url_name.split(':')[1]
        else:
            self.url_name = url_name
        try:
            self.label = label.title()
        except AttributeError:
            self.label = None

        self.title = title or self.label or self.name.title()  # the anchor title

        self.active = active
        self.html_id = html_id or self.name
        self.glyphicon = glyphicon
        self.fa_icon = fa_icon
        if self.fa_icon and self.fa_icon.startswith('fa-'):
            self.fa_icon = f'fa {self.fa_icon}'
        self.icon = icon
        self.icon_height = icon_height
        self.icon_width = icon_width
        if not self.url_name:
            raise NavbarItemError(
                f'\'url_name\' not specified. See {repr(self)}')
        elif self.url_name == '#':
            self.reversed_url = '#'
        else:
            self.reversed_url = reverse(self.url_name)
        if permission_codename:
            try:
                app_label, codename = permission_codename.split('.')
            except ValueError:
                app_label = 'edc_navbar'
                codename = permission_codename
            else:
                if app_label != 'edc_navbar':
                    raise NavbarItemError(
                        f'Invalid navbar permission_codename. Expected app_label '
                        f'to be \'edc_navbar\'. Got \'{permission_codename}\'')
            finally:
                permission_codename = f'{app_label}.{codename}'
        self.permission_codename = permission_codename

    def __repr__(self):
        return (f'{self.__class__.__name__}(name={self.name}, '
                f'title={self.title}, url_name={self.url_name})')

    def __str__(self):
        return f'{self.name}, {self.url_name}'

    def get_context(self, selected_item=None, **kwargs):
        """Returns a dictionary of context data.
        """
        context = copy.copy(self.__dict__)
        context.update(**kwargs)
        if selected_item == self.name or self.active:
            context.update(active=True)
        return context

    def render(self, request=None, **kwargs):
        """Render to string the template and context data.

        If permission codename is specified, check the user
        has permissions. If not return a disabled control.
        """
        context = self.get_context(**kwargs)
        if not self.permission_codename:
            context.update(has_navbar_item_permission=True)
        else:
            context.update(
                has_navbar_item_permission=request.user.has_perm(
                    self.permission_codename))
        return render_to_string(
            template_name=self.template_name,
            context=context)
