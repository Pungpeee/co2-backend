from celery import shared_task
from rest_framework import status

from account_log.models import AccountLog
from alert.models import Alert
from log.models import Log
from utils.account.check_account_wallet import get_access
from utils.account.delete_account_request import delete_account_bc
from utils.base_task import BaseAlertTask
from .models import Account, KYCAccount


@shared_task(bind=True, base=BaseAlertTask)
def task_delete_account(self, alert_id, account_id):
    alert = Alert.objects.filter(id=alert_id).first()
    if not alert:
        return None
    alert.task_id = self.request.id
    alert.status = 2
    alert.save(update_fields=['task_id', 'status', 'datetime_update'])
    account = Account.objects.get(id=account_id)
    if not account:
        alert.set_failed(traceback='Have something wrong with account while delete process')
        return None
    sol_account_key = account.sol_public_key
    bsc_account_key = account.bsc_public_key
    data = get_access(account.id)
    if data and 'public_key' in data and data['public_key']['sol'] == sol_account_key and data['public_key']['bsc'] == bsc_account_key:
        result = delete_account_bc(account.id)
        if not result:
            alert.set_failed(traceback='Delete unsuccessful in BC')

        account.external_id = None
        account.code = None
        account.username = None
        account.email = None
        account.title = 0
        account.first_name = 'Account'
        account.first_name_thai = 'Account'
        account.middle_name = ''
        account.middle_name_thai = ''
        account.last_name = 'Deleted'
        account.last_name_thai = 'Deleted'
        account.id_card = None
        account.laser_code = None
        account.id_front_image = None
        account.id_back_image = None
        account.id_selfie_image = None
        account.image = None
        account.gender = 0
        account.is_admin = False
        account.is_operator = False
        account.phone = None
        account.is_get_news = False
        account.is_share_data = False
        account.count_age = -1
        account.date_birth = None
        account.extra = '{}'
        account.is_active = False
        account.is_accepted_active_consent = False
        account.save()
        KYCAccount.objects.filter(account_id=account.id).delete()
        alert.status = 3
        alert.traceback = 'This account %s already deleted' % account_id
        alert.save(update_fields=['traceback', 'status', 'datetime_update'])

        acc_log = AccountLog.objects.filter(account_id=account.id).last()
        if acc_log:
            acc_log.status = 2
            acc_log.save(update_fields=['status'])

    else:
        alert.set_failed(
            traceback='Delete Account %s unsuccessful, because user have difference wallet address' % account_id
        )
    return 'DONE'