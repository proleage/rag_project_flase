from pydantic import Field
from pydantic_settings import BaseSettings


class DeploymentConfig(BaseSettings):
    """
    Configuration settings for application deployment
    """

    APPLICATION_NAME: str = Field(
        description="Name of the application, used for identification and logging purposes",
        default="langgenius/dify",
    )

    DEBUG: bool = Field(
        description="Enable debug mode for additional logging and development features",
        default=False,
    )

    EDITION: str = Field(
        description="Deployment edition of the application (e.g., 'SELF_HOSTED', 'CLOUD')",
        default="SELF_HOSTED",
    )

    DEPLOY_ENV: str = Field(
        description="Deployment environment (e.g., 'PRODUCTION', 'DEVELOPMENT'), default to PRODUCTION",
        default="PRODUCTION",
    )

    BASE_DIR: str = Field(
        description="The absolute path of Project"
    )

    DATA_INPUT_DIR: str = Field(
        description="Choose Which directory contains input data based on BASE_DIR",
        default="/data_resource/raw_data",
    )

    DATA_OUTPUT_DIR: str = Field(
        description="choose Which directory contains output data based on BASE_DIR",
        default="/data_resource/output_data",
    )


