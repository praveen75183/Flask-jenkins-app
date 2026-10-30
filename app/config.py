import os


class BaseConfig:
    APP_NAME = os.getenv("APP_NAME", "flask-jenkins-app")
    APP_VERSION = os.getenv("APP_VERSION", "dev")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    TESTING = False
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class TestingConfig(BaseConfig):
    TESTING = True
    LOG_LEVEL = "WARNING"


class ProductionConfig(BaseConfig):
    pass


_CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name=None):
    name = name or os.getenv("APP_ENV", "production")
    return _CONFIGS.get(name, ProductionConfig)
