from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)
CredentialsDependency = Annotated[HTTPAuthorizationCredentials | None, Depends(security)]


def get_current_user(credentials: CredentialsDependency) -> dict:
    """Firebase-ready auth dependency.

    In production, verify the bearer token with firebase_admin.auth.verify_id_token.
    Local development accepts an omitted token and marks the user as demo.
    """
    if credentials is None:
        return {"uid": "demo-user", "roles": ["analyst"]}
    if credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")
    return {"uid": "firebase-user", "roles": ["analyst"]}
