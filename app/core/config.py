import os
from dotenv import load_dotenv

load_dotenv()


def read_secret(path: str) -> str:
    with open(path, "r") as f:
        return f.read().strip()


class Settings:
    DB_USER: str = os.environ["DB_USER"]
    DB_NAME: str = os.environ["DB_NAME"]
    INSTANCE_CONNECTION_NAME: str = os.environ["INSTANCE_CONNECTION_NAME"]
    ENV: str = os.environ["ENV"]

    @property
    def DB_PASSWORD(self):
        # Local development
        env_password = os.getenv("DB_PASSWORD")
        if env_password:
            return env_password

        # Cloud Run secret mount
        return read_secret("/secrets/password/db_password")

    @property
    def SECRET_KEY(self):
        # Local development
        env_jwt_secret = os.getenv("SECRET_KEY")
        if env_jwt_secret:
            return env_jwt_secret

        # Cloud Run secret mount
        return read_secret("/secrets/jwt/jwt_secret")
    ALGORITHM = os.environ["ALGORITHM"]


settings = Settings()
