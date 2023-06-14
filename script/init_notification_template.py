import os
import sys

import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'co2.settings')
django.setup()

from notification_template.models import Trigger, Template
from django.conf import settings

trigger_list = [
    {
        "code": "top_up",
        "name": "Top-up",
        "available_param": "{{ prefix }},{{ status }},{{ body }}",
        "available_subject": "{{ prefix }},{{ status }}",
        "available_body": "{{ body }}",
        "is_active": True,
        "action": 2,
        "template_list": [
            {
                "is_standard": True,
                "subject": "Your {{ prefix }} request {{ status }}",
                "body": "{{ body }}"
            }]
    },
    {
        "code": "withdrawal",
        "name": "Withdrawal",
        "available_param": "{{ values }},{{ coin_name }}",
        "available_subject": "{{ values }},{{ coin_name }}",
        "available_body": "{{ values }},{{ coin_name }}",
        "is_active": True,
        "action": 2,
        "template_list": [
            {
                "is_standard": True,
                "subject": "You withdraw {{ values }} {{ coin_name }}",
                "body": "You withdraw {{ values }} {{ coin_name }}"
            }]
    },
    {
        "code": "login_noti",
        "name": "Login Notification Alert",
        "available_param": "{{ ip }}",
        "available_subject": "",
        "available_body": "{{ ip }}",
        "is_active": True,
        "action": 2,
        "template_list": [
            {
                "is_standard": True,
                "subject": "Login Notification",
                "body": "Your account has been logged in at IP Address {{ ip }}"
            }]
    },
    {
        "code": "kyc_approved",
        "name": "KYC Approved",
        "available_param": "",
        "available_subject": "",
        "available_body": "",
        "is_active": True,
        "action": 2,
        "template_list": [
            {
                "is_standard": True,
                "subject": "Your identity verification has been approved",
                "body": "Congratulations! Your submission has been approved"
            }]
    },
    {
        "code": "kyc_rejected",
        "name": "KYC Rejected",
        "available_param": "{{ body }}",
        "available_subject": "",
        "available_body": "{{ body }}",
        "is_active": True,
        "action": 2,
        "template_list": [
            {
                "is_standard": True,
                "subject": "Your identity verification has been rejected",
                "body": '{{ body }}'
            }]
    },
    {
        "code": "kyc_pending",
        "name": "KYC Pending",
        "available_param": "",
        "available_subject": "",
        "available_body": "",
        "is_active": True,
        "action": 2,
        "template_list": [
            {
                "is_standard": True,
                "subject": "Your identity verification has been submitted",
                "body": "Your submission will be queued and processed within 1-15 days."
            }]
    },
    {
        "code": "earn_coin",
        "name": "Earn Coin",
        "available_param": "{{ carbon_saving }},{{ values }},{{ coin }},{{ activity_name }}",
        "available_subject": "",
        "available_body": "{{ carbon_saving }},{{ values }},{{ coin }},{{ activity_name }}",
        "is_active": True,
        "action": 2,
        "template_list": [
            {
                "is_standard": True,
                "subject": "Hooray!",
                "body": "You just dropped {{ activity_name }}, Now you saved {{ carbon_saving }} kg CO2 of carbon and got {{ values }} {{ coin }}"
            }]
    },
]

if __name__ == '__main__':
    for _trigger in trigger_list:

        trigger = Trigger.objects.filter(code=_trigger['code']).first()
        if trigger is None:
            template_id_list = []
            standard_template = None
            custom_template = None
            for template in _trigger['template_list']:
                if template['is_standard']:
                    standard_template = Template.objects.create(**template)
                else:
                    custom_template = Template.objects.create(**template)

            _trigger.pop('template_list')
            _trigger['current_template'] = standard_template
            trigger, is_created = Trigger.objects.get_or_create(**_trigger)
            if standard_template:
                standard_template.event_trigger_id = trigger.id
                standard_template.save(update_fields=['event_trigger'])
            if custom_template:
                custom_template.event_trigger_id = trigger.id
                custom_template.save(update_fields=['event_trigger'])

        else:
            standard_template = Template.objects.filter(is_standard=True, event_trigger=trigger).first()
            if standard_template:
                for template in _trigger['template_list']:
                    if template['is_standard']:
                        standard_template.subject = template['subject']
                        standard_template.body = template['body']
                        standard_template.save(update_fields=['subject', 'body'])

            trigger.available_param = _trigger['available_param']
            trigger.available_subject = _trigger['available_subject']
            trigger.available_body = _trigger['available_body']
            trigger.save(update_fields=['available_param', 'available_subject', 'available_body'])