from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from term.models import Term, Consent
from .serializers import TermSerializer, ConsentSerializer


class TermViewAllowAll(viewsets.GenericViewSet):
    queryset = Term.objects.none()
    serializer_class = TermSerializer
    permission_classes = (AllowAny,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.published_term = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.published_term = self.get_queryset().last()

    def get_queryset(self):
        return Term.objects.filter(
            content_type_id=settings.CONTENT_TYPE('term.term').id,
            is_publish=True
        ).order_by('revision')

    def list(self, request):
        if self.published_term is None:
            return Response(status=status.HTTP_404_NOT_FOUND, data='There are not any published terms.')
        term = self.published_term
        serializer = self.get_serializer(term)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def is_publish(self, request):
        term = self.published_term
        is_publish = True if term is not None and term.is_publish else False
        return Response(data={'is_publish': is_publish}, status=status.HTTP_200_OK)


class TermView(viewsets.GenericViewSet):
    queryset = Term.objects.none()
    serializer_class = TermSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.published_term = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.published_term = self.get_queryset().last()

    def get_queryset(self):
        return Term.objects.filter(
            content_type_id=settings.CONTENT_TYPE('term.term').id,
            is_publish=True).order_by(
            'revision'
        )

    @action(methods=['GET'], detail=False)
    def accept(self, request):
        if self.published_term is None:
            return Response(status=status.HTTP_404_NOT_FOUND, data='There are not any published terms.')
        term = self.published_term

        if Consent.objects.filter(account=request.user, term=term).exists():
            if not request.user.is_accepted_active_consent:
                request.user.is_accepted_active_consent = True
                request.user.save(update_fields=['is_accepted_active_consent'])
                request.user.cache_delete()
            return Response(status=status.HTTP_202_ACCEPTED, data='There are already consent of this term %d' % term.id)
        consent = Consent.objects.create(
            account=request.user,
            term=term,
        )
        request.user.is_accepted_active_consent = True
        request.user.save(update_fields=['is_accepted_active_consent'])
        return Response(data=ConsentSerializer(consent).data, status=status.HTTP_200_OK)

