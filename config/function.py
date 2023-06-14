import urllib
import json
import ast
import uuid

from config.models import Config


class ConfigFunction(object):

    @staticmethod
    def execute(function_name, data=None):
        try:
            method_to_call = getattr(ConfigFunction, function_name)
            if data:
                try:
                    data = json.loads(data)
                except:
                    try:
                        data = ast.literal_eval(data)
                    except:
                        data = None
            return method_to_call(data)
        except:
            return None

    @staticmethod
    def redirect_azure(data=None):
        config_login_backend = int(Config.pull_value('config-login-backend'))
        result = {'url': None, 'url_logout': None}
        if config_login_backend == 1:
            azure_config = Config.pull('config-login-azure').value_text
            if isinstance(azure_config, str):
                azure_config = ast.literal_eval(azure_config)
            if azure_config.get('type') == 'msal':
                return result
            azure_config.update(
                {
                    'redirect_url': Config.pull_value('config-site-url'),
                    'nonce': uuid.uuid4()
                }
            )
            url_authorize_login = '{site}/{tenant}/{path_authorize}?scope={scope}&client_id={' \
                                  'client_id}&response_mode={response_mode}&response_type={response_type}&nonce={' \
                                  'nonce}&state={state}&redirect_url={redirect_url}'.format(**azure_config)
            url_authorize_logout = '{site}/{tenant}/oauth2/logout/'.format(**azure_config)

            result = {
                'url': url_authorize_login,
                'url_logout': url_authorize_logout
            }
        return result

    @staticmethod
    def redirect_oauth(data=None):
        oauth_config = Config.pull_value('config-login-oauth-grant-code')
        result = {'url': '', 'url_mobile': ''}
        partner = int(Config.pull_value('config-login-oauth-grant-code-partner'))

        if partner == 1:  # admd
            oauth_config.update(
                {
                    'client_id': urllib.parse.quote(oauth_config.get('client_id')),
                    'redirect_uri': '%s/account/validate/' % Config.pull_value('config-site-url'),
                }
            )
            url_authorize = '{site}/{path_authorize}?' \
                            'scope={scope}' \
                            '&client_id={client_id}' \
                            '&response_type={response_type}' \
                            '&redirect_uri={redirect_uri}'.format(**oauth_config)

            url_authorize_mobile = '{site}/{path_authorize}?' \
                            'scope={scope}' \
                            '&client_id={client_id_mobile}' \
                            '&response_type={response_type}' \
                            '&redirect_uri={redirect_uri}'.format(**oauth_config)

            result = {
                'url': url_authorize,
                'url_mobile': url_authorize_mobile
            }
        return result

    @staticmethod
    def register_redirect(data=None):
        result = {'url': ''}
        if data:
            result = data
        else:
            config_login_backend = int(Config.pull_value('config-login-backend'))
            if config_login_backend == 7:
                oauth_config = Config.pull_value('config-login-oauth-grant-code')
                partner = int(Config.pull_value('config-login-oauth-grant-code-partner'))

                if partner == 1:  # admd
                    oauth_config.update(
                        {
                            'client_id': urllib.parse.quote(oauth_config.get('client_id')),
                            'redirect_uri': '%s/account/validate/' % Config.pull_value('config-site-url'),
                        }
                    )

                    url_register = '{site}/{path_authorize}?' \
                                    'scope={scope}' \
                                    '&client_id={client_id}' \
                                    '&response_type={response_type}' \
                                    '&redirect_uri={redirect_uri}' \
                                    '&template_name={index_register}'.format(**oauth_config)

                    result['url'] = url_register
        return result