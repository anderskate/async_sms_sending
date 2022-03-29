from pydantic import BaseSettings


class Config(BaseSettings):
    """Settings for app."""
    SMSC_LOGIN: str
    SMSC_PASSWORD: str
    SMSC_SENDER: str
    PHONES: str
    REDIS_URL: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
