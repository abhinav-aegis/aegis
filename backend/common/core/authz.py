from backend.common.models.user_model import User

def is_authorized(actor: User, action: str, resource, **kwargs):
    return True
