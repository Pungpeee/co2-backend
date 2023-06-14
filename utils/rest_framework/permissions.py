from rest_framework.permissions import BasePermission

from config.models import Config


class DenyAny(BasePermission):
    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False


class ViewDashboardPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False

        if request.user.has_perm('dashboard.view_dashboard', group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        # print('call: has_object_permission', view, obj.id)
        return True


class ViewPermission(object):

    def has_permission(self, request, view):
        request.is_view = False
        request.is_organization = False
        request.is_department = False
        request.is_level = False
        request.is_group = False
        request.is_provider = False
        request.is_instructor = False
        request.is_support = False
        request.is_inspector = False
        request.is_mentor = False
        request.is_manager = False

        if request.user is None or not request.user.is_authenticated:
            return False

        # A = app name
        # P = permission name
        # M = model name (lowercase)
        # A.P_M
        # content_request.view_contentrequest
        print(view.app, view.model)
        if request.user.has_perm('%s.view_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            request.is_view = True
            return True
        elif request.user.has_perm(
                '%s.view_by_organization_%s' % (view.app, view.model),
                group=request.AUTH_GROUP
        ) or request.user.has_perm(
            '%s.view_org_%s' % (view.app, view.model),
            group=request.AUTH_GROUP
        ):
            request.is_organization = True
            return True
        elif request.user.has_perm(
                '%s.view_by_department_%s' % (view.app, view.model),
                group=request.AUTH_GROUP
        ):
            request.is_department = True
            return True
        elif request.user.has_perm(
                '%s.view_by_level_%s' % (view.app, view.model),
                group=request.AUTH_GROUP
        ):
            request.is_level = True
            return True
        elif request.user.has_perm(
                '%s.view_by_group_%s' % (view.app, view.model),
                group=request.AUTH_GROUP
        ):
            request.is_group = True
            return True
        elif request.PROVIDER and request.user.has_perm(
                '%s.view_by_provider_%s' % (view.app, view.model),
                group=request.AUTH_GROUP
        ):
            request.is_provider = True
            return True
        elif request.INSTRUCTOR and request.user.has_perm(
                '%s.view_by_instructor_%s' % (view.app, view.model),
                group=request.AUTH_GROUP
        ):
            request.is_instructor = True
            return True
        elif request.user.has_perm(
                '%s.view_by_support_%s' % (view.app, view.model),
                group=request.AUTH_GROUP
        ):
            request.is_support = True
            return True
        elif request.user.has_perm(
                '%s.view_by_inspector_%s' % (view.app, view.model),
                group=request.AUTH_GROUP
        ):
            request.is_inspector = True
            return True
        elif request.user.has_perm(
                '%s.view_by_mentor_%s' % (view.app, view.model),
                group=request.AUTH_GROUP
        ):
            request.is_mentor = True
            return True
        elif request.user.has_perm(
                '%s.view_by_manager_%s' % (view.app, view.model),
                group=request.AUTH_GROUP
        ):
            request.is_manager = True
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class IsSuperAdmin(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_superuser)


class ViewContentCheckinPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.view_content_check_in_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class ViewTokenPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        
        if request.user.has_perm('%s.view_token_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class AddPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.add_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


# class ApproveContentPermission(object):
#     def has_permission(self, request, view):
#         if request.user is None or not request.user.is_authenticated:
#             return False
#         
#         if request.user.has_perm('%s.approve_content_%s' % (view.app, view.model), group=request.AUTH_GROUP):
#             return True
#         else:
#             return False
#
#     def has_object_permission(self, request, view, obj):
#         return True


class ChangePermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.change_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class ChangeProgressPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.change_progress_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class ChangePublishPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.change_publish_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class ChangeCertificatePermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.change_certificate_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class ChangeTransactionPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.change_transaction_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class ChangeAccountPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.change_account_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class ChangeContentCheckinPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.change_content_check_in_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class CancelContentPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.cancel_content_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class DeletePermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.delete_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class CancelRequestPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.cancel_request_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class ViewFormPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.view_form_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class ExportPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.export_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True


class UnauthorizedPermission(object):
    def has_permission(self, request, view):
        from django.conf import settings

        if request.user.is_authenticated or settings.IS_EXPLORE:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        return True


# ref: ClickUp - 7hyzrr
class DeleteMaterialPermission(object):
    def has_permission(self, request, view):
        if request.user is None or not request.user.is_authenticated:
            return False
        
        if request.user.has_perm('%s.delete_material_%s' % (view.app, view.model), group=request.AUTH_GROUP):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return True
