from django.db.models import Subquery
from account.models import Account


class PermissionAccountManager(object):
    view_permission_list = [
        'is_view',
        'is_department',
        'is_group',
        'is_inspector',
        'is_instructor',
        'is_level',
        'is_manager',
        'is_mentor',
        'is_organization',
        'is_provider',
        'is_support',
    ]
    request = None
    _function_dict = {}
    _filter_dict = {}
    _exclude_dict = {}
    _extend_dict = {}
    _key = None
    _user = None
    _account_queryset = None

    def __init__(
            self,
            request,
            view_permission_list=None,
            function_dict=None,
            filter_dict=None,
            exclude_dict=None,
            extend_dict=None,
            key=None,
            user=None
    ):
        self._function_dict = {
            'is_view': self._get_all_list,
            'is_inspector': self._get_empty_list,
            'is_instructor': self._get_all_list,
            'is_provider': self._get_all_list,
            'is_support': self._get_empty_list,
        }

        if view_permission_list:
            self.view_permission_list = view_permission_list
        if function_dict:
            self._function_dict.update(function_dict)
        if filter_dict:
            self._filter_dict = filter_dict
        if exclude_dict:
            self._exclude_dict = exclude_dict
        if extend_dict:
            self._extend_dict = extend_dict
        if request:
            self.request = request
            self._user = self.request.user
            self._set_key()
        else:
            self._user = user
            self._key = key

    def get_user(self):
        return self._user

    def get_key(self):
        return self._key

    def _get_empty_list(self):
        return []

    def _get_all_list(self):
        return Account.objects.all()

    def _set_key(self):
        for key in self.view_permission_list:
            if getattr(self.request, key, False):
                self._key = key
                break

    def _get_account_id_list(self):
        function = self._function_dict.get(self._key, self._get_all_list)
        self._account_queryset = function()

    def _filter_by_parameter(self):
        '''
        this function use for filter. example:
            - view_by_department get only account active account
            - view_by_group filter account by is_active
            - other view_by ignore filtering fileds active
                filter_dict = {
                    'is_department': {'is_active': True},
                    'is_group': {'is_active': False},
                }
            - view_by_department get only some account
                filter_dict = {
                    'is_department': {'id__in': [1,2,3]}
                }
        '''
        parameter = self._filter_dict.get(self._key, {})
        if parameter:
            self._account_queryset = self._account_queryset.filter(**parameter)

    def _extend_by_parameter(self):
        '''
        this function use for extend. example:
        - view_by_department extend 1 user
            extend_dict = {
                'is_department': {'id': 1},
            }
        '''
        parameter = self._extend_dict.get(self._key, {})
        if parameter:
            self._account_queryset = self._account_queryset | Account.objects.filter(**parameter)

    def _exclude_by_parameter(self):
        '''
            this function use for remove. example:
            - view_by_department remove 1 user
                exclude_dict = {
                    'is_department': {'id': 1},
                }
         '''
        parameter = self._exclude_dict.get(self._key, {})
        if parameter:
            self._account_queryset = self._account_queryset.exclude(**parameter)

    def get_account_queryset(self):
        self._get_account_id_list()
        self._filter_by_parameter()
        self._exclude_by_parameter()
        self._extend_by_parameter()
        return self._account_queryset
