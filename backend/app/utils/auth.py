from fastapi.security import HTTPBearer
from fastapi import Response, HTTPException, status
from firebase_admin import auth
from app.api.deps import AccessTokenDeps

security = HTTPBearer(auto_error=False)


def decode_access_token(
    res: Response,
    id_token: AccessTokenDeps,
) -> dict:
    """Use firebase admin to verify a JWT token from FireBase Auth client.

    Args:
        res (Response): The response.
        id_token (Annotated[HTTPAuthorizationCredentials, Depends): User credentials.

    Raises:
        HTTPException: _description_

    Returns:
        str: The decoded token.
    """
    try:
        decoded_token = auth.verify_id_token(id_token.credentials)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user"
        )
    res.headers['WWW-Authenticate'] = 'Bearer realm="auth_required"'
    return decoded_token


async def get_current_user(
    token
):
    return None
