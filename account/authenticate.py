from config.models import Config
from .models import Account


class EmailModelBackend(object):

    def authenticate(self, request, username=None, password=None, account_id=None):

        def _both():
            return Account.pull_account(username)

        if username is None and password is None and account_id is not None:
            account = Account.objects.filter(id=account_id).first()
        else:
            config = Config.pull('account-login-key')
            if username is None:
                return None

            if config:
                if config.value == 'username':
                    account = Account.objects.filter(username=username).first()
                elif config.value == 'email':
                    account = Account.objects.filter(email=username).exclude(email__isnull=True).first()
                else:
                    account = _both()
            else:
                account = _both()

        if account is not None:
            if password is None:
                return account
            elif account.check_password(password):
                return account
        return None


    def get_user(self, user_id):
        try:
            return Account.pull(user_id)
        except Account.DoesNotExist:
            return None
