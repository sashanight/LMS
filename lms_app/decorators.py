from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from .models import *


@require_http_methods(["GET", "POST"])
def check_token(request):
    try:
        access_token = None
        if request.method == "POST":
            access_token = AccessToken.objects.get(token=request.POST['token'])

        if request.method == "GET":
            access_token = AccessToken.objects.get(token=request.GET['token'])

        if access_token.date_login < datetime.datetime.now() - datetime.timedelta(hours=12):
            access_token.delete()
            return None

        user_id = access_token.user_id
        return user_id
    except:
        pass
    return None


def is_authenticated(fn):
    def decorator(request):
        uid = check_token(request)
        if uid is not None:
            return fn(uid, request)
        else:
            return HttpResponse(status=401)
    return decorator
