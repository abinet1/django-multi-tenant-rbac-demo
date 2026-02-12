from django.urls import path
from .views import BootstrapAdminInvitationView, ManagerInvitationView, InvitationAcceptView

urlpatterns = [
    path('invitations/bootstrap-admin/', BootstrapAdminInvitationView.as_view(), name='bootstrap_admin_invite'),
    path('invitations/', ManagerInvitationView.as_view(), name='manager_invite'),
    path('invitations/accept/', InvitationAcceptView.as_view(), name='invitation_accept'),
]
