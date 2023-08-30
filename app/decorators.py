from django.http import HttpResponseForbidden

def user_is_admin(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_admin:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("You don't have permission to access this page.")
        else:
            return HttpResponseForbidden("You are not authenticated.")
    return _wrapped_view

def user_is_alumni(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_alumni:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("You don't have permission to access this page.")
        else:
            return HttpResponseForbidden("You are not authenticated.")
    return _wrapped_view

def user_is_superuser(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("You don't have permission to access this page.")
        else:
            return HttpResponseForbidden("You are not authenticated.")
    return _wrapped_view
