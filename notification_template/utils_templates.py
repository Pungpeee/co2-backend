from django.conf import settings
from django.http import JsonResponse
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response

from account.models import Account
from activity.models import CarbonActivity
from analytic.models import Session
from config.models import Config
from log.models import Log
from transaction.models import Transaction
from utils.datetime import convert_to_local
from rest_framework.exceptions import MethodNotAllowed

### if need to send None back just {None}
def get_data(trigger_code, account, content_type, content_id, content_list=[]):
    site_url = settings.CO2_API_URL
    header_image = Config.pull_value('mailer-header-image')
    query_str = ''
    prefix = Config.pull_value('mailer-subject-prefix')

    if trigger_code == 1:  # Direct Message
        return render_to_string(
            'mailer/inbox/direct_message.html',
            {
                'image_url': settings.CO2_API_URL + header_image,
                'title': '',
                'body': '',
            }
        )
    elif trigger_code == 'top_up':
        if content_type.id == settings.CONTENT_TYPE('transaction.transaction').id:
            transaction = Transaction.objects.filter(id=content_id).first()
            datetime_update =convert_to_local(transaction.datetime_update).strftime('%d %b %Y, %H:%M')
            '''
                overwrite body for support CR from PM and manage it done in row
                sent notification not relate with init_noti  will replace it before sent to notification to client)
            '''
            if transaction.status == 2:
                return {
                    'prefix': 'Top-up',
                    'status': 'has been completed',
                    'body': 'You have bought %s %s @ %s THB' % (
                        transaction.values,
                        transaction.get_coin_display(),
                        transaction.thb_values,
                    )
                }
            elif transaction.status == -1:
                return {
                    'prefix': 'Top-up',
                    'status': 'is pending',
                    'body': 'The process will be completed within 24 hours'
                }
            elif transaction.status == 1:
                return {
                    'prefix': 'Top-up',
                    'status': 'Waiting for payment',
                    'body': 'You have bought %s %s @ %s THB' % (
                        transaction.values,
                        transaction.get_coin_display(),
                        transaction.thb_values,
                    )
                }
            elif transaction.status == -2:
                return {
                    'prefix': 'Top-up',
                    'status': 'has been rejected',
                    'body': '%s \r\n\r\n' % datetime_update +\
                            'Your request for a top-up %s THB has been rejected\r\n' % transaction.thb_values +\
                            'due to one of the following reasons: \r\n\r\n' +\
                            ' 1. Bank account name is different from account name% datetime_update\r\n' +\
                            ' 2. Amount you transferred is mismatched with amount on order ticket\r\n\r\n' +\
                            'Please check your email for further instruction'
                }

    elif trigger_code == 'withdrawal':
        if content_type.id == settings.CONTENT_TYPE('transaction.transaction').id:
            transaction = Transaction.objects.filter(id=content_id).first()
            # if not transaction or transaction.account.id is not account.id or transaction.method != 5:
            #     Log.push(None, 'TRANSACTION_NOTI',
            #                      'NOTIFICATION_WRONG', account, 'Have something wrong with this transaction',
            #                      status.HTTP_200_OK, content_type=content_type, content_id=content_id)
            #     return
            return {
                'values': transaction.values,
                'coin_name': transaction.get_coin_display()
            }

    elif trigger_code == 'login_noti':
        session = Session.objects.filter(account_id=account.id).order_by('-datetime_create').first()
        return {
            'ip': session.ip
        }

    elif trigger_code == 'kyc_approved':
        return {None}

    elif trigger_code == 'kyc_rejected':
        if content_type.id == settings.CONTENT_TYPE('account.account').id:
            account = Account.objects.filter(id=account.id, is_active=True).first()
            datetime_update = convert_to_local(account.datetime_update).strftime('%d %b %Y, %H:%M')
            return {
                'body': '%s \r\n\r\n' % datetime_update + \
                        'Your identity verification has been rejected due to one of the following reasons:\r\n\r\n' + \
                        ' 1. Incorrect document submission\r\n' + \
                        ' 2. Unclarified attached photo of your identity documents\r\n' + \
                        ' 3. Unclarified attached photo of your selfie\r\n\r\n' + \
                        'Please resubmit your KYC through\r\n www.carbonwallet.co.th or Carbon Wallet Application'
            }
    elif trigger_code == 'kyc_pending':
        if content_type.id == settings.CONTENT_TYPE('account.account').id:
            return {None}

    elif trigger_code == 'earn_coin':
        if content_type.id == settings.CONTENT_TYPE('activity.carbonactivity').id:
            coin_dict = dict(CarbonActivity.COIN_CHOICES)
            carbon_activity = CarbonActivity.objects.get(id=content_id)
            return {
                'activity_name': carbon_activity.activity_name.title(),
                'carbon_saving': carbon_activity.carbon_saving,
                'values': carbon_activity.values,
                'coin': coin_dict[carbon_activity.coin]
            }
