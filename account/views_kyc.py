from django.conf import settings
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from azure.storage.blob import BlobServiceClient
from datetime import datetime

from account.models import KYCStep1, KYCStep2, KYCStep3
from .serializers_kyc import KYCStep1Serializer, KYCStep2Serializer, KYCStep3Serializer


class KYCStep1View(viewsets.GenericViewSet):
    queryset = KYCStep1.objects.all()
    serializer_class = KYCStep1Serializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            kyc = KYCStep1.objects.get(account=request.user)
        except KYCStep1.DoesNotExist:
            print(data)
            try:
                data['account'] = request.user
                kyc = KYCStep1.objects.create(**data)
                serializer = KYCStep1Serializer(kyc)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(data={'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = KYCStep1Serializer(kyc, data=data, partial=True)
        serializer.is_valid()
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        try:
            kyc = KYCStep1.objects.get(account=request.user)
        except Exception as e:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = KYCStep1Serializer(kyc)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class KYCStep2View(viewsets.GenericViewSet):
    queryset = KYCStep2.objects.all()
    serializer_class = KYCStep2Serializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            kyc = KYCStep2.objects.get(account=request.user)
        except KYCStep2.DoesNotExist:
            print(data)
            try:
                data['account'] = request.user
                kyc = KYCStep2.objects.create(**data)
                serializer = KYCStep2Serializer(kyc)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(data={'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = KYCStep2Serializer(kyc, data=data, partial=True)
        serializer.is_valid()
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        try:
            kyc = KYCStep2.objects.get(account=request.user)
        except Exception as e:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = KYCStep2Serializer(kyc)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False, url_path='upload')
    def upload(self, request, *args, **kwargs):
        file_split = str(request.FILES["file"].name).split(".")
        file_type = f'.{file_split[len(file_split)-1]}'
        file_name = f'{request.user.id}-kyc2-{datetime.now().isoformat()}{file_type}'
        try:
            connect_str = settings.AZURE_STORAGE_CONNECTION_STRING

            blob_service_client = BlobServiceClient.from_connection_string(connect_str)
            blob_client = blob_service_client.get_blob_client(container='vekin-cero-blob-nonprod',
                                                              blob=file_name)
            try:
                blob_client.upload_blob(request.FILES['file'].file.read())
            except Exception as e:
                print('error while upload to blob')
                print(e)
            return Response(data={'file': f'{file_name}'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(data={'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KYCStep3View(viewsets.GenericViewSet):
    queryset = KYCStep3.objects.all()
    serializer_class = KYCStep3Serializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            kyc = KYCStep3.objects.get(account=request.user)
        except KYCStep3.DoesNotExist:
            print(data)
            try:
                data['account'] = request.user
                kyc = KYCStep3.objects.create(**data)
                serializer = KYCStep3Serializer(kyc)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(data={'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = KYCStep3Serializer(kyc, data=data, partial=True)
        serializer.is_valid()
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        try:
            kyc = KYCStep3.objects.get(account=request.user)
        except Exception as e:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = KYCStep3Serializer(kyc)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
