import os
import bleach
from django.conf import settings
from django.core.exceptions import ValidationError
from config.models import Config


def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


def validate_pdf_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', ]
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


def validate_excel_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.xlsx', '.xls']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


def validate_doc_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.doc', '.docx']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


def validate_account_phone(value):
    if not value.isdigit():
        raise ValidationError(u'Invalid phone number')

    th_phone_config = Config.pull_value('config-th-phone-number')
    if not th_phone_config:
        if len(value) < 10 or len(value) > 11:
            raise ValidationError(u'Invalid phone number')

    country_code = th_phone_config['country_code']
    prefix = th_phone_config['prefix']
    number_length = th_phone_config['suffix_number_length']

    if value.startswith(country_code):
        if len(value[len(country_code):]) != number_length:
            raise ValidationError(u'Invalid phone number')
    elif value.startswith(prefix):
        if len(value[len(prefix):]) != number_length:
            raise ValidationError(u'Invalid phone number')
    else:
        raise ValidationError(u'Invalid phone number')


def validate_html_tags(value):
    return bleach.clean(value,
                        tags=settings.BLEACH_ALLOWED_TAGS,
                        attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
                        styles=settings.BLEACH_ALLOWED_STYLES,
                        protocols=settings.BLEACH_ALLOWED_PROTOCOLS)

