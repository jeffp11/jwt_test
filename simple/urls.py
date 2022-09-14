from django.contrib import admin
from django.urls import path

from simple.views import TokenView, ReTokenView, app_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', ReTokenView.as_view(), name='token_refresh'),
    path('api/app/', app_view, name='post app'),
]
