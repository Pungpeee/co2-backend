from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from guardian.models import UserObjectPermission

from account.models import Account
from .views import check_permission


@user_passes_test(check_permission)
def guardian_view(request):
    account = request.user
    content_type = None
    if request.method == 'POST':
        account = Account.objects.filter(email__istartswith=request.POST.get('account', )).first()
        content_type = settings.CONTENT_TYPE_ID(int(request.POST.get('content_type', -1)))
    user_object_permission_list = UserObjectPermission.objects.filter(
        user=account,
        content_type=content_type
    )
    return render(
        request,
        'console/guardian.html',
        {
            'NAVBAR': 'guardian',
            'account': account,
            'user_object_permission_list': user_object_permission_list,
            'content_type_event': settings.CONTENT_TYPE('event.event')
        }
    )