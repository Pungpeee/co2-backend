from django.conf import settings
from django.http import HttpResponse, FileResponse
from rest_framework import viewsets, mixins, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import base64

from .models import Account
from .serializers import AccountPartnerSerializer


class AccountFileView(APIView):
    serializer_class = None
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = request.GET
        if not data.get('name', None):
            return Response(data={'detail': 'file is require'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            connect_str = settings.AZURE_STORAGE_CONNECTION_STRING

            blob_service_client = BlobServiceClient.from_connection_string(connect_str)
            container_client = blob_service_client.get_container_client(container='vekin-cero-blob-nonprod')
            blob = container_client.download_blob(data['name'])
            read = blob.read()
            response = HttpResponse(read, content_type="image/jpeg")
            return response
        except Exception as e:
            print(e)
            return Response(data={'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
