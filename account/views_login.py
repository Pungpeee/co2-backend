from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from account.views_login_vekin import login_vekin
from .models import Account
from .serializers import LoginSerializer


class LoginView(viewsets.GenericViewSet):
    queryset = Account.objects.all()
    allow_redirects = True
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data, status_response = login_vekin(request, data, 'WEB_VEKIN', True)
        return Response(data=data, status=status_response)
