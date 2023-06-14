from django.contrib.auth import logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import Session
from log.models import Log


class LogoutView(APIView):

    def post(self, request):
        account_id = request.user.id
        session_key = request.session.session_key
        user = request.user if request.user.is_authenticated else None
        Log.push(request, 'ACCOUNT', 'ACCOUNT_LOGOUT', user,
                 'Logout success', status.HTTP_200_OK)
        logout(request)
        Session.remove(account_id, session_key)
        return Response(status=status.HTTP_200_OK)

    def get(self, request):
        account_id = request.user.id
        session_key = request.session.session_key
        user = request.user if request.user.is_authenticated else None
        Log.push(request, 'ACCOUNT', 'ACCOUNT_LOGOUT', user, 'Logout success', status.HTTP_200_OK)
        logout(request)
        Session.remove(account_id, session_key)
        return Response(status=status.HTTP_200_OK)
