from celery import shared_task
from django.conf import settings
from infobip_api_client.api_client import ApiClient, Configuration
from infobip_api_client.model.sms_advanced_textual_request import SmsAdvancedTextualRequest
from infobip_api_client.model.sms_destination import SmsDestination
from infobip_api_client.model.sms_response import SmsResponse
from infobip_api_client.model.sms_textual_message import SmsTextualMessage
from infobip_api_client.api.send_sms_api import SendSmsApi
from infobip_api_client.exceptions import ApiException
from rest_framework import status

from account.models import Account, KYCAccount, IdentityVerification
from alert.models import Alert
from config.models import Config
from log.models import Log


@shared_task(bind=True)
def task_sent_verification_infobip(self, account_id, recipient, code, ref_code, alert_id):
    alert = Alert.objects.filter(id=alert_id).first()
    account = Account.objects.get(id=account_id)
    kyc_account = KYCAccount.objects.filter(account_id=account_id).first()
    identity = IdentityVerification.objects.filter(account_id=account.id, status=1).first()
    alert.task_id = self.request.id
    alert.status = 2
    alert.save(update_fields=['task_id', 'status', 'datetime_update'])

    BASE_URL = settings.INFOBIP_BASE_URL
    API_KEY = settings.INFOBIP_API_KEY

    SENDER = Config.pull_value('config-sms-sender-name')
    RECIPIENT = recipient
    MESSAGE_TEXT = "Your OTP Code : %s \n(Ref : %s). \nOTP will be expired within 5 mins" % (code, ref_code)

    client_config = Configuration(
            host= BASE_URL,
            api_key={"APIKeyHeader": API_KEY},
            api_key_prefix={"APIKeyHeader": "App"},
        )

    api_client = ApiClient(client_config)

    sms_request = SmsAdvancedTextualRequest(
            messages=[
                SmsTextualMessage(
                    destinations=[
                        SmsDestination(
                            to=RECIPIENT,
                        ),
                    ],
                    _from=SENDER,
                    text=MESSAGE_TEXT,
                )
            ])

    api_instance = SendSmsApi(api_client)
    try:
        api_response = api_instance.send_sms_message(sms_advanced_textual_request=sms_request)
        Log.push(None, 'KYC_ACCOUNT', 'VERIFICATION', account,
                 'Sent verification success', status.HTTP_200_OK, note=str(api_response))
        alert.status = 3
        alert.save(update_fields=['status', 'datetime_update'])
    except ApiException as ex:
        api_response = api_instance.send_sms_message(sms_advanced_textual_request=sms_request)
        Log.push(None, 'KYC_ACCOUNT', 'VERIFICATION', account,
                 'Sent verification fail', status.HTTP_400_BAD_REQUEST, note=str(api_response))
        alert.set_failed(traceback=api_response)
        kyc_account.is_mobile_verify = False
        kyc_account.phone = ''
        kyc_account.save(update_fields=['is_mobile_verify', 'phone'])
        account.phone = ''
        account.save(update_fields=['phone', 'datetime_update'])
        identity.status = -1
        identity.save(update_fields=['status'])
        alert.status = -1
        alert.save(update_fields=['status', 'datetime_update'])
        return ex
