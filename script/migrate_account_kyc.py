import os
import sys

import django
from datetime import date

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'co2.settings')
django.setup()

from account.models import Account, KYCAccount


if __name__ == '__main__':
    for account in Account.objects.all():
        kyc_acc = KYCAccount.objects.filter(account_id=account.id).first()
        if kyc_acc:
            print(kyc_acc.account_id, kyc_acc.first_name, kyc_acc.last_name, 'Already Create')
            continue
        else:
            account_kyc = KYCAccount.objects.create(
                account_id=account.id,
                title = account.title,
                first_name = account.first_name,
                first_name_thai = account.first_name_thai,
                middle_name = account.middle_name,
                middle_name_thai = account.middle_name_thai,
                last_name = account.last_name,
                last_name_thai = account.last_name_thai,
                id_card = account.id_card,
                laser_code = account.laser_code,
                id_front_image = account.id_front_image,
                id_back_image = account.id_back_image,
                id_selfie_image = account.id_selfie_image,
                is_accepted_kyc_consent = account.is_accepted_kyc_consent,
                kyc_status = account.kyc_status,
                phone = account.phone,
                date_birth = account.date_birth
            )
            print(account_kyc.account_id, account_kyc.first_name, account_kyc.last_name, 'Done')
