from django.conf import settings


def sso(request):  # noqa: ARG001 Django passes the request to every context processor
    """
    Tells the login pages whether to offer the login with OpenID Connect, which is the case once
    SOCIAL_AUTH_OIDC_OIDC_ENDPOINT is set, and how to label its button (VOLUCRA_SSO_LABEL)
    """
    return {
        "use_sso": bool(getattr(settings, "SOCIAL_AUTH_OIDC_OIDC_ENDPOINT", None)),
        "sso_label": getattr(settings, "VOLUCRA_SSO_LABEL", "Volucra SSO"),
    }
