# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

app_name = 'products'
urlpatterns = [
    url(r'^$', views.ProductListView.as_view(), name='list'),
]
