from rest_framework import status
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        code = _get_error_code(response.data)
        response.data = {
            "detail": "Sua sessao expirou ou o token de acesso e invalido. Faca login novamente.",
            "code": code or "authentication_failed",
            "action": "login_required",
        }

    return response


def _get_error_code(data):
    if isinstance(data, dict):
        value = data.get("code")
        if value:
            return str(value)

        messages = data.get("messages")
        if isinstance(messages, list) and messages:
            first = messages[0]
            if isinstance(first, dict) and first.get("token_type"):
                return "token_not_valid"

    return None
