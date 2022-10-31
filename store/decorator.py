#from django.http import Http404
from django.core.exceptions import PermissionDenied

def check_user_able_to_see_page(*groups):

    def decorator(function):
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(name__in=groups).exists():
                return function(request, *args, **kwargs)
            #raise Http404
            raise PermissionDenied
        return wrapper

    return decorator