import logging

from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict, BaseSettings

DEBUG = False

def configure_logging():
    LOG_FORMAT = "%(asctime)s %(levelname)s : %(message)s : %(pathname)s : %(funcName)s : %(lineno)d"
    logging.basicConfig(format=LOG_FORMAT, level=logging.WARN, filename="log.txt", filemode="a")

class Settings(BaseSettings):
    gigachat_llm_token: SecretStr
    gigachat_max_tokens: SecretStr
    gigachat_model: SecretStr
    host: SecretStr
    port: SecretStr
    urls_list_file_name: SecretStr
    cors_origins: SecretStr
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

env_config = Settings()
LLM_TOKEN = env_config.gigachat_llm_token.get_secret_value()
MAX_TOKENS = env_config.gigachat_max_tokens.get_secret_value()
MODEL = env_config.gigachat_model.get_secret_value()
HOST = env_config.host.get_secret_value()
PORT = env_config.port.get_secret_value()
URLS_LIST_FILE_NAME = env_config.urls_list_file_name.get_secret_value()
CORS_ORIGINS = env_config.cors_origins.get_secret_value().split(",")
