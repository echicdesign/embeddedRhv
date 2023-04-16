from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from .models import Shop
from shopify.utils import shop_url

import binascii
import json
import os
import re
import shopify


class LoginView(View):
    print("views.LoginView")
    def get(self, request, *args, **kwargs):
        if request.GET.get("shop"):
            return authenticate(request)
        return render(
            request, "shopify_app/login.html", {"app_name": "Sample Django app"}
        )

    def post(self, request):
        return authenticate(request)


def callback(request):
    print("views.callback")
    params = request.GET.dict()
    shop = params.get("shop")

    try:
        validate_params(request, params)
        access_token, access_scopes = exchange_code_for_access_token(request, shop)
        store_shop_information(access_token, access_scopes, shop)
        after_authenticate_jobs(shop, access_token)
    except ValueError as exception:
        messages.error(request, str(exception))
        return redirect(reverse("login"))

    redirect_uri = build_callback_redirect_uri(request, params)


    print("views.callback.return")

    return redirect(redirect_uri)


@csrf_exempt
def uninstall(request):
    print("views.uninstall")
    uninstall_data = json.loads(request.body)
    shop = uninstall_data.get("domain")
    Shop.objects.filter(shopify_domain=shop).delete()
    print("views.uninstall.return")

    return HttpResponse(status=204)


# Login helper methods


def authenticate(request):
    print("views.authenticate")
    try:
        shop = get_sanitized_shop_param(request)
        scopes, redirect_uri, state = build_auth_params(request)
        store_state_param(request, state)

        print("shop | "+str(shop))
        print("scopes | "+str(scopes))
        print("redirect_uri | "+str(redirect_uri))
        print("state | "+str(state))

        permission_url = _new_session(shop).create_permission_url(
            scopes, redirect_uri, state
        )

        # print("permission_url | "+str(permission_url))

        # print("views.authenticate.return1")
        permission_url = permission_url.replace("None","4171-122-61-79-235.ngrok-free.app")
        return redirect(permission_url)

# 068b-122-61-79-235.ngrok-free.app

# /admin/oauth/authorize?client_id=db751166a9535eb61be522bc06ba0dc4&scope=write_products,write_orders&redirect_uri
# =https://localhost:8008/auth/shopify/callback
# &state=80e0f1aaa115dbd968b56156f0bdbe




    except ValueError as exception:
        messages.error(request, str(exception))
        print("views.authenticate.return2")
        return redirect(reverse("login"))


def get_sanitized_shop_param(request):
    print("views.get_sanitized_shop_param")
    sanitized_shop_domain = shop_url.sanitize_shop_domain(
        request.GET.get("shop", request.POST.get("shop"))
    )
    if not sanitized_shop_domain:
        raise ValueError("Shop must match 'example.myshopify.com'")
    print("views.get_sanitized_shop_param.return")
    return sanitized_shop_domain


def build_auth_params(request):
    print("views.build_auth_params")
    scopes = get_configured_scopes()
    redirect_uri = build_redirect_uri()
    state = build_state_param()
    print("views.build_auth_params.return")

    return scopes, redirect_uri, state


def get_configured_scopes():
    print("views.get_configured_scopes")
    return apps.get_app_config("shopify_app").SHOPIFY_API_SCOPES.split(",")


def build_redirect_uri():
    print("views.build_redirect_uri")
    app_url = apps.get_app_config("shopify_app").APP_URL
    callback_path = reverse("callback")
    print("views.build_redirect_uri.return")
    return "https://{app_url}{callback_path}".format(
        app_url=app_url, callback_path=callback_path
    )


def build_state_param():
    print("views.build_state_param")
    return binascii.b2a_hex(os.urandom(15)).decode("utf-8")


def store_state_param(request, state):
    print("views.store_state_param")
    request.session["shopify_oauth_state_param"] = state


def _new_session(shop_url):
    print("views._new_session")
    print("shop_url|    "                +   str(shop_url))
    shopify_api_version             =   apps.get_app_config("shopify_app").SHOPIFY_API_VERSION
    shopify_api_key                 =   apps.get_app_config("shopify_app").SHOPIFY_API_KEY
    shopify_api_secret              =   apps.get_app_config("shopify_app").SHOPIFY_API_SECRET
    print("shopify_api_version| "    +   str(shopify_api_version))
    # print("shopify_api_key| "        +   str(shopify_api_key))
    # print("shopify_api_secret|  "     +   str(shopify_api_secret))
    shopify.Session.setup(api_key=shopify_api_key, secret=shopify_api_secret)
    print("views._new_session.return")
    return shopify.Session(shop_url, shopify_api_version)

# Callback helper methods


def validate_params(request, params):
    print("views.validate_params")
    validate_state_param(request, params.get("state"))
    if not shopify.Session.validate_params(params):  # Validates HMAC
        raise ValueError("Invalid callback parameters")


def validate_state_param(request, state):
    print("views.validate_state_param")
    if request.session.get("shopify_oauth_state_param") != state:
        raise ValueError("Anti-forgery state parameter does not match")

    request.session.pop("shopify_oauth_state_param", None)


def exchange_code_for_access_token(request, shop):
    print("views.exchange_code_for_access_token")
    session = _new_session(shop)
    access_token = session.request_token(request.GET)
    access_scopes = session.access_scopes
    print("views.exchange_code_for_access_token.return")

    return access_token, access_scopes


def store_shop_information(access_token, access_scopes, shop):
    print("views.store_shop_information")
    shop_record = Shop.objects.get_or_create(shopify_domain=shop)[0]
    shop_record.shopify_token = access_token
    shop_record.access_scopes = access_scopes

    shop_record.save()


def build_callback_redirect_uri(request, params):
    print("in views build_callback_redirect_uri")
    base = request.session.get("return_to", reverse("root_path"))
    return "{base}?shop={shop}".format(base=base, shop=params.get("shop"))


# callback after_authenticate_jobs helper methods


def after_authenticate_jobs(shop, access_token):
    print("views.after_authenticate_jobs")
    create_uninstall_webhook(shop, access_token)


def create_uninstall_webhook(shop, access_token):
    print("views.create_uninstall_webhook")
    with shopify_session(shop, access_token):
        app_url = apps.get_app_config("shopify_app").APP_URL
        webhook = shopify.Webhook()
        webhook.topic = "app/uninstalled"
        webhook.address = "https://{host}/uninstall".format(host=app_url)
        webhook.format = "json"
        webhook.save()


def shopify_session(shopify_domain, access_token):
    print("views.shopify_session")

    api_version = apps.get_app_config("shopify_app").SHOPIFY_API_VERSION
    return shopify.Session.temp(shopify_domain, api_version, access_token)
