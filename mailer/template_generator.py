from datetime import datetime

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from config.models import Config
from mailer.tasks import send_mail


# Send only is_subscribe = True


class ForgetPasswordUser:
    def __init__(self):
        pass

    @staticmethod
    def create_forget_user_password(full_name, email, token, site_url, method=1):
        prefix = Config.pull_value('mailer-subject-prefix')
        header_image = Config.pull_value('mailer-header-image')
        mail_icon_image = Config.pull_value('mailer-icon-image')
        subject = '%s - Reset Password' % prefix
        _dt = (datetime.now()).strftime('%H:%M:%S')
        link = site_url + '/reset-password?token=%s&method=%s' % (token, method)

        body = render_to_string('mailer/account/confirm_reset_password_email.html',
                                {
                                    'full_name': full_name,
                                    'date_time': _dt,
                                    'email': email,
                                    'link': link,
                                    'header_image': settings.CO2_API_URL + header_image,
                                    'mail_icon': settings.CO2_API_URL + mail_icon_image
                                }
                                )
        send_mail(email, subject, body, 1)

    @staticmethod
    def create_forget_user_password_otp(email, token, age):
        prefix = Config.pull_value('mailer-subject-prefix')
        header_image = Config.pull_value('mailer-header-image')
        subject = '%s - Reset Password' % prefix
        body = render_to_string('mailer/account/reset_password_otp.html',
                                {'email': email, 'header_image': settings.CO2_API_URL + header_image, 'token': token, 'age': age})

        send_mail(email, subject, body, 1, is_queue=False)


class IdentificationOTPMail:

    def __init__(self):
        pass

    @staticmethod
    def create_identification_otp(email, token, content_name, identification_otp):
        prefix = Config.pull_value('mailer-subject-prefix')
        header_image = Config.pull_value('mailer-header-image')
        subject = '%s - OTP Verification %s' % (prefix, content_name)
        body = render_to_string('mailer/inbox/identification_otp.html',
                                {'header_image': settings.CO2_API_URL +  header_image,
                                 'token': token
                                 })

        send_mail(email, subject, body, 2, is_queue=True)
        identification_otp.datetime_send = timezone.now()
        identification_otp.save(update_fields=['datetime_send'])
