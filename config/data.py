from django.conf import settings

CONFIG_DICT = {
    'config-app-name': {
        'app': 'config',
        'is_web': True,
        'is_dashboard': True,
        'type': 2,
        'value': 'CO2 Wallet',
        'sort': 0,
    },
    'config-is-enable-facebook-authentication': {
        'app': 'account',
        'is_web': True,
        'is_dashboard': True,
        'type': 1,
        'value': True,
        'sort': 1,
    },
    'config-is-enable-google-authentication': {
        'app': 'account',
        'is_web': True,
        'is_dashboard': True,
        'type': 1,
        'value': False,
        'sort': 2,
    },
    'config-login-backend': {
        'app': 'account',
        'is_web': True,
        'is_dashboard': True,
        'type': 6,
        'value': 0,
        'value_text': '0:default',
        'sort': 3,
    },
    'config-session-age': {
        'app': 'config',
        'is_web': True,
        'is_dashboard': True,
        'type': 3,
        'value': 86400 * 365,  # Day.
        'sort': 4,
    },
    'config-account-password-expire': {
        'app': 'account',
        'is_web': False,
        'is_dashboard': False,
        'type': 1,
        'value': False,
        'sort': 5,
    },
    'config-account-age-password': {
        'app': 'account',
        'is_dashboard': False,
        'is_web': False,
        'type': 3,
        'value': '180',  # Days
        'sort': 6,
    },
    'config-is-enable-register': {
        'app': 'account',
        'is_web': True,
        'is_dashboard': True,
        'type': 1,
        'value': True,
        'sort': 7,
    },
    'config-is-enable-apple-id-authentication': {
        'app': 'account',
        'is_web': True,
        'is_dashboard': True,
        'type': 1,
        'value': 1,
        'sort': 8,
    },
    'config-apple-auth-client-id': {
        'app': 'account',
        'is_web': True,
        'is_dashboard': False,
        'type': 2,
        'value': '',
        'sort': 9,
    },
    'config-register-form': {
        'app': 'account',
        'is_web': True,
        'is_dashboard': False,
        'type': 10,
        'value': {},
        'value_text': {
            'field_list': [{
                'key': 'username',
                'name': 'username',
                'placeholder': 'username',
                'type': 5,
                'max_length': 255,
                'min_length': 4,
                'is_optional': False
            }, {
                'key': 'email',
                'name': 'email',
                'placeholder': 'email',
                'type': 5,
                'max_length': 255,
                'is_optional': False
            }, {
                'key': 'password',
                'name': 'password',
                'placeholder': 'password',
                'type': 5,
                'is_optional': False
            }, {
                'key': 'confirm_password',
                'name': 'confirm_password',
                'placeholder': 'confirm_password',
                'type': 5,
                'is_optional': False
            }, {
                'key': 'first_name',
                'name': 'first_name',
                'placeholder': 'first_name',
                'type': 5,
                'max_length': 255,
                'is_optional': True
            }, {
                'key': 'last_name',
                'name': 'last_name',
                'placeholder': 'last_name',
                'type': 5,
                'max_length': 255,
                'is_optional': True
            }]
        },
        'sort': 11,
    },
    'config-register-form-co2': {
        'app': 'account',
        'is_web': True,
        'is_dashboard': False,
        'type': 10,
        'value': {},
        'value_text': {
            'field_list': [{
                'key': 'email',
                'name': 'email',
                'placeholder': 'email',
                'type': 5,
                'max_length': 255,
                'is_optional': False
            }, {
                'key': 'password',
                'name': 'password',
                'placeholder': 'password',
                'type': 5,
                'is_optional': False
            }, {
                'key': 'confirm_password',
                'name': 'confirm_password',
                'placeholder': 'confirm_password',
                'type': 5,
                'is_optional': False
            }]
        },
        'sort': 11,
    },
    'config-login-oauth-grant-code': {
        'app': 'config',
        'is_web': False,
        'is_dashboard': False,
        'type': 10,
        'value': {},
        'value_text': {
            'site': '',
            'path_authorize': '',
            'path_token': '',
            'client_id': '',
            'client_secret': '',
            'grant_type': 'authorization_code',
            'response_type': 'code',
            'scope': '',
            'state': '',
            'nonce': ''
        },
        'sort': 12,
    },
    'config-account-condition-password': {
        'app': 'account',
        'is_dashboard': True,
        'is_web': True,
        'type': 10,
        'value': {
        },
        'value_text': {
            'condition_length': {
                'name': 'length',
                'is_use': True,
                'message_error': '',
                'compile': '.{8}'
            },
            'condition_upper': {
                'name': 'upper',
                'is_use': False,
                'message_error': '',
                'compile': '[A-Z]',
            },
            'condition_lower': {
                'name': 'lower',
                'is_use': False,
                'message_error': '',
                'compile': '[a-z]',
            },
            'condition_symbol': {
                'name': 'symbol',
                'is_use': False,
                'message_error': '',
                'compile': '\W',
            },
            'condition_number': {
                'name': 'number',
                'is_use': False,
                'message_error': '',
                'compile': '[0-9]',
            }
        },
        'sort': 13,
    },
    'config-password-history': {
        'app': 'config',
        'is_web': False,
        'is_dashboard': False,
        'type': 3,
        'value': 0,
        'sort': 14
    },
    'notification-client-list': {
        'app': 'notification',
        'is_web': False,
        'is_dashboard': False,
        'type': 10,
        'value': {},
        'value_text': {
            'app_name': 'fcm_django',
            'model': 'FCMDevice',
            'service': '',
            'app_list': ['*'],
            'settings': {
                'FCM_SERVER_KEY': [
                    'AAAASZJ40Uc:APA91bEwnDuwFAisXZtVcyzgZQWjJw6WVWkIWVM3vbi8dBeR88EPZOkcsnxYcOOXxHT6e_DH5LuiIO_ArCUlKIi1mO6q0kDBMVjjd9OZWCtzA3QcxLGwg1Jr0d3tE2hFs4r1NO_30ukE'
                ],
                'ONE_DEVICE_PER_USER': False,
                'DELETE_INACTIVE_DEVICES': False,
            }
        },
        'sort': 15,
    },
    'notification-email-list': {
        'app': 'notification',
        'is_web': False,
        'is_dashboard': False,
        'type': 10,
        'value': {},
        'value_text': {
            'app_name': 'mailer',
            'model': 'Mailer',
            'service': 'SMTP',  # FWD, DJANGO, MAILGUN --> 'config-mailer-mailgun-token'
            'app_list': ['*'],
            'settings': {
                'EMAIL_HOST': 'smtp.gmail.com',
                'EMAIL_HOST_ALIAS': 'System',
                'EMAIL_HOST_USER': 'noreply@vekin.co.th',
                'EMAIL_HOST_PASSWORD': 'Vekin123!',
                'EMAIL_SERVICE': 'SMTP',
                'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
                'EMAIL_PORT': 587,
                'EMAIL_USE_TLS': True,
                'EMAIL_USE_AUTH': True,
            }
        },
        'sort': 16,
    },
    'config-mailer-mailgun-token': {
        'app': 'mailer',
        'is_web': False,
        'is_dashboard': False,
        'type': 10,
        'value': {'site': '', 'key': '', 'from': 'vekin@gmail.com'},
        'sort': 17
    },
    'config-mailer-is-enable': {
        'app': 'mailer',
        'is_web': True,
        'is_dashboard': False,
        'type': 1,
        'value': True,
        'sort': 18
    },
    'config-site-url': {
        'app': 'config',
        'is_web': False,
        'is_dashboard': False,
        'type': 2,
        'value': '',
        'sort': 19,
    },
    'mailer-subject-prefix': {
        'app': 'mailer',
        'is_web': False,
        'is_dashboard': False,
        'type': 2,
        'value': 'CO2 platform',
        'sort': 20,
    },
    'mailer-header-image': {
        'app': 'mailer',
        'is_web': False,
        'is_dashboard': False,
        'type': 8,
        'image': '/_default/mailer/header.png',
        'sort': 21,
    },
    'mailer-icon-image': {
        'app': 'mailer',
        'is_web': False,
        'is_dashboard': False,
        'type': 8,
        'image': '/_default/mailer/mail_icon.png',
        'sort': 22,
    },
    'mailer-from-email': {
        'app': 'mailer',
        'is_web': False,
        'is_dashboard': False,
        'type': 2,
        'value': '',
        'sort': 23
    },

    'config-account-forgot-password-otp-age': {
        'app': 'account',
        'is_web': False,
        'is_dashboard': False,
        'type': 3,
        'value': 300,  # second
        'sort': 24,
    },

    # DEEP LINK
    'config-site-url-app-link': {
        'app': 'config',
        'is_web': False,
        'is_dashboard': False,
        'type': 2,
        'value': 'https://co2-api-uat.vekin.co.th/backend/api/',
        'sort': 25,
    },

    'config-th-phone-number': {
        'app': 'account',
        'is_web': False,
        'is_dashboard': False,
        'type': 10,
        'value_text': {
            'country_code': '66',
            'prefix': '0',
            'suffix_number_length': 9
        },
        'sort': 26,
    },
    'config-verify-email-is-enabled': {
        'app': 'config',
        'is_web': True,
        'is_dashboard': False,
        'type': 1,
        'value': True,
        'sort': 27,
    },
    'config-verification-expired-time': {
        'app': 'config',
        'is_web': True,
        'is_dashboard': False,
        'type': 3,
        'value': 15,  # Minutes
        'value_text': '**Minutes',
        'sort': 28,
    },
    'config-verify-email-is-enabled': {
        'app': 'config',
        'is_web': True,
        'is_dashboard': False,
        'type': 1,
        'value': False,
        'sort': 29,
    },
    'config-cero-coin-per-bath': {
        'app': 'config',
        'is_web': True,
        'is_dashboard': True,
        'type': 10,
        'value_text': {
            'CERO': 1,
            'THB': 1
        },
        'sort': 30,
    },
    'config-carbon-saving-is-enabled': {
        'app': 'account',
        'is_web': True,
        'is_dashboard': False,
        'type': 1,
        'value': False,
        'sort': 31
    },
    'notification-device-list': {
        'app': 'inbox',
        'is_web': False,
        'is_dashboard': False,
        'type': 9,
        'value': 'mail,fcm',
        'sort': 32,
    },
    'config-carbon-activity-enable': {
        'app': 'activity',
        'is_web': False,
        'is_dashboard': False,
        'type': 1,
        'value': True,
        'sort': 33,
    },
    'block-chain-enable': {
        'app': 'co2',
        'is_web': False,
        'is_dashboard': False,
        'type': 1,
        'value': True,
        'sort': 33,
    },
    'scb_pg_enable': {
        'app': 'co2',
        'is_web': False,
        'is_dashboard': False,
        'type': 1,
        'value': True,
        'sort': 34,
    },
    'config-verification-expired-time': {
        'app': 'config',
        'is_web': True,
        'is_dashboard': False,
        'type': 3,
        'value': 5,  # Minutes
        'value_text': '**Minutes',
        'sort': 35,
    },
    'config-is-enable-infobip': {
        'app': 'account',
        'is_web': True,
        'is_dashboard': True,
        'type': 1,
        'value': True,
        'sort': 36,
    },
    'config-sms-sender-name': {
        'app': 'config',
        'is_web': True,
        'is_dashboard': True,
        'type': 2,
        'value': 'IBTEST',
        'sort': 37,
    },
    'config-swap-enable':{
        'app': 'transaction',
        'is_web': True,
        'is_dashboard': True,
        'type': 1,
        'value': True,
        'sort': 38,
    },
    'config-account-forgot-password-otp-failed-limit': {
        'app': 'account',
        'is_web': False,
        'is_dashboard': False,
        'type': 3,
        'value': 5,  # times
        'sort': 39,
    },
}
