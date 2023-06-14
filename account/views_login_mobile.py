from account.views_login_vekin import login_vekin
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Account
from .serializers import LoginSerializer


class LoginMobileView(viewsets.GenericViewSet):
    queryset = Account.objects.all()
    allow_redirects = True
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data_response, status_response = login_vekin(request, data, 'MOBILE_VEKIN', False)

        return Response(data_response, status=status_response)
