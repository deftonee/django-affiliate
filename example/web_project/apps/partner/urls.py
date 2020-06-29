# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'partner'
urlpatterns = [
    url(r'^$', login_required(views.AffiliateView.as_view()), name='affiliate'),
]
