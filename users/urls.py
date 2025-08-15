from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from .apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path("users/", views.UserListCreateAPIView.as_view(), name="users"),
    path(
        "users/<int:pk>/", views.UserRetrieveUpdateDestroyAPIView.as_view(), name="user"
    ),
    path("login/", views.MyToken.as_view(), name="login"),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=[AllowAny]),
        name="token-refresh",
    ),
    path("payments/", views.PaymentListCreateAPIView.as_view(), name="payments"),
    path(
        "payments/<int:pk>/",
        views.PaymentRetrieveUpdateDestroyAPIView.as_view(),
        name="payment",
    ),
]
