from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class IsAuthenticatedView(APIView):
    serializer_class = None
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        return Response({
            'is_authenticated': request.user.is_authenticated
        })
