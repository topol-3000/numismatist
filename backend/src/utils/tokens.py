import secrets
import string


def generate_share_token(length: int = 32) -> str:
    """Generate a secure random token for sharing collections."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
