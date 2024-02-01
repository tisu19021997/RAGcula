from typing import Annotated
from fastapi.security import HTTPBearer
from fastapi import Response, HTTPException, status
from firebase_admin import auth as firebase_auth

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

security = HTTPBearer(auto_error=False)


def decode_access_token(
    res: Response,
    id_token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict:
    """Use firebase admin to verify a JWT token from FireBase Auth client."""
    try:
        decoded_token = firebase_auth.verify_id_token(id_token.credentials)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user"
        )
    res.headers['WWW-Authenticate'] = 'Bearer realm="auth_required"'
    return decoded_token
