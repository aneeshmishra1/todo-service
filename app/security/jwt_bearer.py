from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from starlette import status

from app.core.config import settings
from app.schemas.user_schema import CurrentUser


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
security = HTTPBearer()


class JWTBearer(HTTPBearer):

    async def __call__(self, request: Request):

        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme")

        token: str = credentials.credentials
        try:
            print(f"inside get_current_user() token: {token}")
            print(f"Secret Key: {SECRET_KEY} and algorithms {ALGORITHM}")
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"payload: {payload}")
            current_user = CurrentUser(user_id=payload.get("user_id"), username=payload.get("username"),
                                       user_role=payload.get("user_role"), token=token)
            if current_user.username is None or current_user.user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Could not validate user **")
            print(
                f"inside get_current_user() username: {current_user.username}, "
                f"user_id: {current_user.user_id}, "
                f"user_role: {current_user.user_role}, "
                f"and token: {token}")
            return current_user
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user")
