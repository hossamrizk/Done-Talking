from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.core import get_settings

security = HTTPBearer()

token = get_settings().API_TOKEN.get_secret_value()


async def get_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """
    Retrieve the API key from query or header.
    """
    if credentials.credentials != token:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized access. Invalid token."
        )
    return credentials.credentials
