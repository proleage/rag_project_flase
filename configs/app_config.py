from pydantic_settings import SettingsConfigDict

from configs.deploy import DeploymentConfig
from configs.feature import HostedServiceConfig
from configs.middleware import MiddlewareConfig
from configs.middleware.cache import RedisConfig
from configs.middleware.vdb import MilvusConfig
from configs.packaging import PackagingInfo


class RagConfig(DeploymentConfig, HostedServiceConfig, MiddlewareConfig, PackagingInfo):
    model_config = SettingsConfigDict(
        # read from dotenv format config file
        env_file=".env",
        env_file_encoding="utf-8",
        # ignore extra attributes
        extra="ignore",
    )
