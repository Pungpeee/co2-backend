from rest_framework.viewsets import GenericViewSet, mixins
from .models import Card
from .serializers import CardSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class CardView(GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        cards = Card.objects.filter(account=request.user)
        serializer = CardSerializer(cards, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
