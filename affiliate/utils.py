# -*- coding: utf-8 -*-
from django.utils.http import urlencode
from django.apps import apps
from urllib.parse import parse_qsl, urlparse, urlunparse
from . import app_settings


def get_affiliate_model():
    return apps.get_model(app_settings.AFFILIATE_MODEL)


def add_affiliate_code(url, aid_code):
    parsed = urlparse(str(url))
    query = dict(parse_qsl(parsed.query))
    query.update({app_settings.PARAM_NAME: str(aid_code)})
    url_parts = list(parsed)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


def remove_affiliate_code(url):
    parsed = urlparse(str(url))
    query = dict(parse_qsl(parsed.query))
    query.pop(app_settings.PARAM_NAME, None)
    url_parts = list(parsed)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)
