from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render


def check_permission(user):
    return user.is_superuser


# @user_passes_test(check_permission)
def home_view(request):
    return render(
        request,
        'console/home.html',
        {
            'version': '0.0001',
        }
    )