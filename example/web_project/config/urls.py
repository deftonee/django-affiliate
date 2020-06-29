# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from django.contrib import admin

# from apps.users.urls import urlpatterns as users_urlpatterns
# from apps.partner.urls import urlpatterns as partner_urlpatterns
# from apps.products.urls import urlpatterns as products_urlpatterns

# from apps import users, partner, products
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^users/', include('apps.users.urls')),
    url(r'^partner/', include('apps.partner.urls')),
    url(r'^$', include('apps.products.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
