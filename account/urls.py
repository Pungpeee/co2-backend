from django.conf.urls import url
from django.urls import include
from django.urls.conf import path
from rest_framework.routers import DefaultRouter, Route

from co2 import settings
from .views_balance import AccountBalanceView
from .views_change_password import ChangePasswordViewSet
from .views_forget_password import ForgetPasswordView
from .views_is_authenticated import IsAuthenticatedView
from .views_login import LoginView
from .views_login_mobile import LoginMobileView
from .views_login_social import LoginSocialView
# from .views_login_sso import LoginSSOView
from .views_logout_mobile import LogoutMobileView
from .views_profile import ProfileView
from .views_register import RegisterView
from .views_reset_password import ResetPasswordView
from .views_token import TokenView
from .views_verify_OTP import VerifyMobileOTPView
from .views_verify_email import VerifyEmailView
from .views import AccountDeleteView, AccountView
from .views_login_card import LoginCardView
from .views_kyc import KYCStep1View, KYCStep2View, KYCStep3View
from .views_partner import PartnerView
# from .views_file import AccountFileView

router = DefaultRouter()
router.include_root_view = settings.ROUTER_INCLUDE_ROOT_VIEW
router.routes[0] = Route(
    url=r'^{prefix}{trailing_slash}$',
    mapping={
        'get': 'list',
        'post': 'create',
        'patch': 'profile_patch',
    },
    name='{basename}-list',
    detail=False,
    initkwargs={'suffix': 'List'}
)

# router.register(r'login/social', LoginSocialView)
router.register(r'login', LoginView)
router.register(r'login/card', LoginCardView)
# router.register(r'login_sso', LoginSSOView)
router.register(r'login/mobile', LoginMobileView)
router.register(r'change/password', ChangePasswordViewSet, basename='account-change-password')
router.register(r'profile', ProfileView)
router.register(r'register', RegisterView)
router.register(r'token', TokenView)
router.register(r'balance', AccountBalanceView)
router.register(r'verify-email', VerifyEmailView)
router.register(r'verify-mobile-OTP', VerifyMobileOTPView)
router.register(r'reset-password', ResetPasswordView, basename='account-reset-password')
router.register(r'forget/password', ForgetPasswordView)
router.register(r'delete', AccountDeleteView)
router.register(r'', AccountView)
router.register(r'kyc-step-1', KYCStep1View)
router.register(r'kyc-step-2', KYCStep2View)
router.register(r'kyc-step-3', KYCStep3View)
router.register(r'partner', PartnerView)
# router.register(r'file', AccountFileView)


urlpatterns = [
    url(r'is-authenticated/$', IsAuthenticatedView.as_view()),
    url(r'logout/mobile/$', LogoutMobileView.as_view()),
    # url(r'logout/$', LogoutView.as_view()),
    # url(r'session/$', SessionView.as_view()),

    url(r'^', include(router.urls)),
]
