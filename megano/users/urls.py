from django.urls import path

from .views import RegisterView, LogOutView, LogInView, ProfileView, ProfileAvatarView, ProfilePassportView

urlpatterns = [
    path('sign-up', RegisterView.as_view(), name="register"),
    path('sign-out', LogOutView.as_view(), name="logout"),
    path('sign-in', LogInView.as_view(), name="login"),
    path('profile/avatar', ProfileAvatarView.as_view(), name="profile-avatar"),
    path('profile/password', ProfilePassportView.as_view(), name="profile-password"),
    path('profile', ProfileView.as_view(), name="profile"),
]
