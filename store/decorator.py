#from django.http import Http404
import functools
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.urls import reverse
def verify_customer():
    ''' verify if the user has customer profile, 
        if not redirect to create a customer profile, 
        whereas the user already has an account 
    '''
    def decorator(function):
        def wrapper(request,*args, **kwargs):
            if request.user.is_anonymous:
                return redirect('login')                
            elif 'customer' in dir(request.user):            
                if request.user.customer.stripe_cus_id!='':
                    return function(request,*args, **kwargs)
                else:
                    messages.info(request,"Introduzca por favor sus datos para poder continuar ")
                    vi = reverse('create_customer_already_signup', kwargs={'pk':str(request.user.id)})
                    return redirect(f'{vi}?next={request.path}')
            else:
                messages.info(request,"Introduzca por favor sus datos para poder continuar ")
                vi = reverse('create_customer_already_signup', kwargs={'pk':str(request.user.id)})
                return redirect(f'{vi}?next={request.path}')
        return wrapper
    return decorator

def Only_Ajax_Req(view_func):
    @functools.wraps(view_func)
    def wrapper(request,*args, **kwargs):
        if request.headers.get('x-requested-with')=='XMLHttpRequest':
            return view_func(request,*args, **kwargs)        
        return HttpResponseBadRequest("can't Process this request ")
    return wrapper

def check_user_able_to_see_page(*groups):
    
    def decorator(function):
        #print('-----fucnc name--------',function.__name__)
        def wrapper(request, *args, **kwargs):
            print('re,args,kwgars',request, args,kwargs)
            if request.user.groups.filter(name__in=groups).exists() | request.user.is_superuser:
                return function(request, *args, **kwargs)
            #raise Http404
            raise PermissionDenied
        return wrapper

    return decorator

def is_vendor():
    def decorator(function):        
        def wrapper(request, *args, **kwargs):            
            if request.user.userprofile.is_vendor:
                return function(request, *args, **kwargs)
            #raise Http404
            #raise PermissionDenied
            messages.add_message(request, messages.WARNING, 'You are not a vendor !')
            return redirect('frontpage')
        return wrapper
    return decorator