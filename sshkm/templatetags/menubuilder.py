import logging

from sshkm.models import Menu, MenuItem
from django import template
from django.core.cache import cache


register = template.Library()


def build_menu(parser, token):
    """
    {% menu menu_name %}
    """
    try:
        tag_name, menu_name = token.split_contents()
    except:
        raise template.TemplateSyntaxError("%r tag requires exactly one argument" % token.contents.split()[0])
    return MenuObject(menu_name)


class MenuObject(template.Node):
    def __init__(self, menu_name):
        self.menu_name = menu_name

    def render(self, context):
        try:
            current_path = context['request'].path
            user = context['request'].user
        except KeyError:
            current_path = None
            user = None

        context['menuitems'] = get_items(self.menu_name, current_path, user)
        return ''
  
def get_items(menu_name, current_path, user):
    """
    If possible, use a cached list of items to avoid continually re-querying 
    the database.
    The key contains the menu name, whether the user is authenticated, and the current path.
    Disable caching by setting MENU_CACHE_TIME to -1.
    """
    from django.conf import settings
    cache_time = getattr(settings, 'MENU_CACHE_TIME', 1800)
    debug = getattr(settings, 'DEBUG', False)

    if user:
        is_authenticated = user.is_authenticated
        is_anonymous = user.is_anonymous
    else:
        is_authenticated = False
        is_anonymous = True

    if cache_time >= 0 and not debug:
        cache_key = 'django-menu-items/%s/%s/%s'  % (menu_name, current_path, is_authenticated)
        menuitems = cache.get(cache_key, [])
        if menuitems:
            return menuitems
    else:
        menuitems = []
        
    menu = Menu.objects.filter(name=menu_name).first()

    if not menu:
        return []

    if (str(user) == 'AnonymousUser' or str(user) == 'None'):
        Items = MenuItem.objects.filter(menu=menu).filter(login_required__lt=1).filter(staff_required__lt=1).order_by('order')
    else:
        if user.is_staff:
            Items = MenuItem.objects.filter(menu=menu).filter(login_required__lte=1).filter(staff_required__lte=1).order_by('order')
        else:
            Items = MenuItem.objects.filter(menu=menu).filter(login_required__lte=1).filter(staff_required__lt=1).order_by('order')

    for i in Items:
        if current_path:
            current = ( i.link_url != '/' and current_path.startswith(i.link_url)) or ( i.link_url == '/' and current_path == '/' )
            if menu.base_url and i.link_url == menu.base_url and current_path != i.link_url:
                current = False
        else:
            current =False

        show_anonymous = i.anonymous_only and is_anonymous
        show_auth = i.login_required and is_authenticated
        if (not (i.login_required or i.anonymous_only)) or (i.login_required and show_auth) or (i.anonymous_only and show_anonymous):
            menuitems.append({'url': i.link_url, 'title': i.title, 'current': current,})

    if cache_time >= 0 and not debug:
        cache.set(cache_key, menuitems, cache_time)
    return menuitems


register.tag('menu', build_menu)