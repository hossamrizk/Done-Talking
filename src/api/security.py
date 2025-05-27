from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader, APIKeyQuery
from core import get_settings

API_KEYS = {
    get_settings().ADMIN_SECRET_KEY: "admin"
}

api_key_query = APIKeyQuery(name="api_key_query", auto_error=False)
api_key_header = APIKeyHeader(name="api_key_header", auto_error=False)

async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header)
):
    """
    Retrieve the API key from query or header.
    """
    if api_key_query in API_KEYS:
        return API_KEYS[api_key_query]
    elif api_key_header in API_KEYS:
        return API_KEYS[api_key_header]
    else:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized access. Check your API key and try again."
        )
