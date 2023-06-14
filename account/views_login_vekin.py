import logging

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.utils import timezone
from rest_framework import status

from account.caches import cached_account_profile
from account.models import Account, Session
from analytic.models import Session as AnalyticSession
from config.models import Config
from log.models import Log
from notification_template.models import Trigger
from utils.ip import get_client_ip


def login_vekin(request, data, code, is_web, group='ACCOUNT_LOGIN'):
    logger = logging.getLogger('LOGIN')
    if not data['password']:
        Log.push(request, group, code, None,
                 'Hacking!! password is None', status.HTTP_401_UNAUTHORIZED)
        logger.info('401 Unauthorized (%s) Password not entered' % data['username'])
        return {'detail': 'error_email_pass_fail'}, status.HTTP_401_UNAUTHORIZED

    account = Account.pull_account(data['username'])
    if not account:
        return {'detail': 'error_email_pass_fail'}, status.HTTP_401_UNAUTHORIZED

    account = authenticate(username=account.username, password=data['password'])
    if account is None:
        _account = Account.pull_account(data['username'].strip().lower())
        if _account:
            Log.push(request, group, code, _account,
                     'Password incorrect', status.HTTP_401_UNAUTHORIZED)
            logger.info('401 Unauthorized (%s) Password Incorrect' % data['username'])
        else:
            Log.push(request, group, code, None,
                     'Username incorrect', status.HTTP_401_UNAUTHORIZED, payload={'username': data['username']})
            logger.info('401 Unauthorized (%s) Username Incorrect' % data['username'])
        return {'detail': 'error_email_pass_fail'}, status.HTTP_401_UNAUTHORIZED

    if not account.is_active:
        Log.push(request, group, code, account, 'User is inactive',
                 status.HTTP_406_NOT_ACCEPTABLE)
        logger.info('406 Not Acceptable (%s) User is inactive' % data['username'])
        return {'detail': 'error_account_inactive'}, status.HTTP_406_NOT_ACCEPTABLE


    if account.is_force_reset_password:
        _data = account.get_token_reset_password(method=2, error='error_account_force_reset_password', device='MOBILE_')
        logger.info('423 Locked (%s) Account Force Reset Password' % data['username'])
        return _data, status.HTTP_423_LOCKED

    if account.check_password_expire:
        _data = account.get_token_reset_password(method=2, error='error_account_password_expired', device='MOBILE_')
        logger.info('423 Locked (%s) Account Password Expired' % data['username'])
        return _data, status.HTTP_423_LOCKED

    login(request, account)
    account.last_active = timezone.now()
    account.save()
    session_key = request.session.session_key
    request.session.set_test_cookie()
    if session_key is None:
        request.session.save()
        session_key = request.session.session_key
    Session.push(request.user, session_key)

    if data['is_remember']:
        request.session.set_expiry(Config.pull_value('config-session-age'))
    else:
        request.session.set_expiry(0)

    if is_web:
        source = 0
    else:
        source = 1
    ip = get_client_ip(request)
    AnalyticSession.push(account, session_key, source, ip)
    Log.push(request, group, code, account, 'Login success', status.HTTP_200_OK)
    Account.send_login_noti(account.email, ip)
    trigger = Trigger.get_code('login_noti')
    trigger.send_notification(
        sender=None,
        inbox_type=1,
        inbox_content_type=settings.CONTENT_TYPE('account.account'),
        inbox_content_id=account.id,
        account_list=[account]
    )
    logger.info('200 OK (%s) Login Success' % data['username'])
    result = cached_account_profile(account.id)

    if is_web:
        # TODO: Flutter issue can't get session id and cstf -token in flutter web
        result.update({
            'sessionid': request.session.session_key,
            'csrftoken': request.META['CSRF_COOKIE']
        })

    return result, status.HTTP_200_OK
