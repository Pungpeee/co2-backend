from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render, redirect
from rest_framework import status

from account.models import Account, KYCAccount
from log.models import Log
from notification_template.models import Trigger


def operator_view(request):
    # TODO Remove later after done, Overwrite flow operator with this flow #2pj76k4
    # Check is admin
    kyc_account = Account.objects.filter(id=request.user.id).first()
    if not kyc_account or not kyc_account.is_operator:
        return redirect('/')

    # Control path here
    page = request.GET.get('page', 1)
    page_type = request.GET.get('page_type', None)

    if not page_type:
        page_type = 'user'

    # Condition
    if page_type == 'user':
        kyc_account_list = list(KYCAccount.objects.order_by('-id'))
        filter_value = request.GET.get('filter_value', '')
        search = request.GET.get('search', '')
        if not kyc_account_list:
            pass
        kyc_account_list = KYCAccount.objects.all()
        if filter_value and filter_value != '-':
            kyc_account_list = kyc_account_list.filter(kyc_status=filter_value)

        if search:
            kyc_account_list = KYCAccount.objects.filter(
                Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(phone__icontains=search) | Q(account__email__icontains=search)
            ).order_by('-id').distinct()
        paginator = Paginator(kyc_account_list, 24)
        try:
            objects = paginator.page(page)
        except PageNotAnInteger:
            objects = paginator.page(1)
        except EmptyPage:
            objects = paginator.page(paginator.num_pages)
        return render(
            request,
            'operator/UserKYC.html',
            {
                'page_type': 'user',
                'account_list': objects if objects else []
            }
        )
    elif page_type == 'user_details':
        account_id = int(request.GET.get('account_id', -1))
        is_approve = int(request.GET.get('is_approve', -1))
        is_reject = int(request.GET.get('is_reject', -1))
        page_type = request.GET.get('page_type', 'user')
        kyc_account = KYCAccount.objects.filter(id=account_id).first()
        account = Account.objects.filter(id=kyc_account.account_id, is_active=True).first()

        # approve
        if is_approve > 0:
            if not account or not kyc_account or kyc_account.kyc_status != 2 or account.kyc_status != 2:
                Log.push(None, 'ACCOUNT_KYC',
                         'ACCOUNT_KYC_WRONG', account, 'Have something wrong with this account',
                         status.HTTP_200_OK, settings.CONTENT_TYPE('account.account'), content_id=account_id)
                return render(request, 'operator/404-not-found.html', {})
            account.kyc_status = 3
            kyc_account.kyc_status = 3
            account.save(update_fields=['kyc_status', 'datetime_update'])
            kyc_account.save(update_fields=['kyc_status'])
            trigger = Trigger.get_code('kyc_approved')
            trigger.send_notification(
                sender=None,
                inbox_type=1,
                inbox_content_type=settings.CONTENT_TYPE('account.account'),
                inbox_content_id=kyc_account.id,
                account_list=[kyc_account]
            )
            Account.send_email_kyc(account.email, 3)
            return redirect('/console/operator')

        # reject
        elif is_reject > 0:
            if not account or not kyc_account or kyc_account.kyc_status != 2 or account.kyc_status != 2:
                Log.push(None, 'ACCOUNT_KYC',
                         'ACCOUNT_KYC_WRONG', account, 'Have something wrong with this account',
                         status.HTTP_406_NOT_ACCEPTABLE, content_type=settings.CONTENT_TYPE('account.account'), content_id=account_id)
                return render(request, 'operator/404-not-found.html', {})
            account.kyc_status = -2
            kyc_account.kyc_status = -2
            account.save(update_fields=['kyc_status', 'datetime_update'])
            kyc_account.save(update_fields=['kyc_status'])
            trigger = Trigger.get_code('kyc_rejected')
            trigger.send_notification(
                sender=None,
                inbox_type=1,
                inbox_content_type=settings.CONTENT_TYPE('account.account'),
                inbox_content_id=kyc_account.id,
                account_list=[kyc_account]
            )
            Account.send_email_kyc(account.email, -2)
            return redirect('/console/operator')
        return render(
            request,
            'operator/UserDetail.html',
            {
                'page_type': page_type,
                'account': kyc_account,
            }
        ) if kyc_account else render(request, 'operator/404-not-found.html', {})

    elif page_type == 'transaction':
        return call_transaction_page(request)

    elif page_type == 'transaction_details':
        transaction_id = int(request.GET.get('transaction_id', -1))
        is_approve = int(request.GET.get('is_approve', -1))
        is_reject = int(request.GET.get('is_reject', -1))
        page_type = request.GET.get('page_type', 'user')
        reason_type = int(request.GET.get('reason_type', 0))

        reason_type_dict = {
            99: '-',
            1: 'Approve with all evident',
            2: 'Mismatching Account Information',
            3: 'Incorrect Amount',
            4: 'Incorrect Receipt'
        }

        transaction = Transaction.objects.filter(id=transaction_id).first()
        payment = None

        if not transaction:
            pass
        else:
            payment = transaction.payment_set.order_by('-datetime_create').first()
            if not payment:
                pass

        if transaction.status == -1 and is_approve > 0:
            # TODO Tranfer coin to user
            url = settings.CO2_CHAIN_API_URL + "transfer/send_token"

            payload = json.dumps({
                "to_address": transaction.account.sol_public_key,
                "account_id": transaction.account.id,
                "token_name": transaction.get_coin_display(),
                "amount": transaction.values
            })

            headers = {
                'authorization': settings.CO2_CHAIN_API_KEY,
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            _data = json.loads(response.text)
            if response.status_code != 200 or response.status_code != 201:
                Log.push(request, 'ACCOUNT', 'TOPUP_COIN', transaction.account, 'Have something wrong with API create wallet',
                         status.HTTP_406_NOT_ACCEPTABLE, payload=response.__dict__)
                return render(request, 'operator/404-not-found.html', {})
            else:
                if _data and _data.get('transaction_hash', None):
                    transaction.transaction_hash = _data.get('transaction_hash')
                if not transaction or transaction.account.id is not kyc_account.id or transaction.method != 3:
                    Log.push(None, 'TRANSACTION_NOTI',
                             'NOTIFICATION_WRONG', kyc_account, 'Have something wrong with this transaction',
                             status.HTTP_200_OK, content_type=settings.CONTENT_TYPE('transaction.transaction'),
                             content_id=transaction_id
                             )
                    return render(request, 'operator/404-not-found.html', {})
                transaction.status = 2
                transaction.desc = reason_type_dict[reason_type]
                transaction.datetime_end = timezone.now()
                transaction.datetime_complete = timezone.now()
                transaction.save(update_fields=['status', 'datetime_end', 'desc', 'datetime_update', 'transaction_hash'])
                Log.push(request, 'ACCOUNT', 'TOPUP_COIN', transaction.account,
                         'Success topup coin', status.HTTP_200_OK, payload=response.__dict__)
                Transaction.send_topup_noti(transaction_id=transaction.id, topup_status=2)
                trigger = Trigger.get_code('top_up')
                trigger.send_notification(
                    sender=None,
                    inbox_type=1,
                    inbox_content_type=settings.CONTENT_TYPE('transaction.transaction'),
                    inbox_content_id=transaction.id,
                    account_list=[transaction.account]
                )
                return call_transaction_page(request)

        elif transaction.status == -1 and is_reject > 0:
            previous_page_type = 'transaction'

            transaction.status = -2
            transaction.desc = reason_type_dict[reason_type]
            transaction.datetime_end = timezone.now()
            transaction.save(update_fields=['status', 'datetime_end', 'desc', 'datetime_update'])
            if transaction.status == -2:
                Log.push(request, 'ACCOUNT', 'TOPUP_COIN', transaction.account,
                         'Reject transaction via reason : %s' % reason_type_dict[reason_type],
                         status.HTTP_200_OK)
            Transaction.send_topup_noti(transaction_id=transaction.id, topup_status=-2)
            trigger = Trigger.get_code('top_up')
            trigger.send_notification(
                sender=None,
                inbox_type=1,
                inbox_content_type=settings.CONTENT_TYPE('transaction.transaction'),
                inbox_content_id=transaction.id,
                account_list=[transaction.account]
            )
            return call_transaction_page(request)

        return render(
            request,
            'operator/TransactionDetail.html',
            {
                'page_type': page_type,
                'transaction': transaction,
                'payment': payment
            }
        ) if account_id and kyc_account else render(request, 'operator/404-not-found.html', {})
    else:
        return render(request, 'operator/404-not-found.html', {})
