"""URL configuration for the locallibrary project."""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Все запросы к catalog/ передаются в urls.py приложения catalog
urlpatterns += [
    path('catalog/', include('catalog.urls')),
]

# Корневой URL перенаправляем на приложение catalog
urlpatterns += [
    path('', RedirectView.as_view(url='/catalog/', permanent=True)),
]

# Страницы аутентификации (login, logout, password_change, password_reset ...)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
