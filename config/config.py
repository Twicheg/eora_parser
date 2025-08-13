import logging

from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict, BaseSettings


def configure_logging():
    LOG_FORMAT = "%(asctime)s %(levelname)s : %(message)s : %(pathname)s : %(funcName)s : %(lineno)d"
    logging.basicConfig(format=LOG_FORMAT, level=logging.WARN, filename="log.txt", filemode="a")

class Settings(BaseSettings):
    llm_token: SecretStr
    urls_list_file_name: SecretStr
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

env_config = Settings()
LLM_TOKEN = env_config.llm_token.get_secret_value()
URLS_LIST_FILE_NAME = env_config.urls_list_file_name.get_secret_value()
