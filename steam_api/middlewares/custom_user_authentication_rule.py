
from steam_api.models.web_user import WebUser, WebUserStatus


def custom_user_authentication_rule(user: WebUser) -> bool:
    return user is not None and user.status == WebUserStatus.ACTIVATED