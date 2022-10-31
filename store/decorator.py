#from django.http import Http404
from django.core.exceptions import PermissionDenied

def check_user_able_to_see_page(*groups):
    print('groupssss',groups)
    def decorator(function):
        print('-----fucnc name--------',function.__name__)
        def wrapper(request, *args, **kwargs):
            print('re,args,kwgars',request, args,kwargs)
            if request.user.groups.filter(name__in=groups).exists() | request.user.is_superuser:
                return function(request, *args, **kwargs)
            #raise Http404
            raise PermissionDenied
        return wrapper

    return decorator