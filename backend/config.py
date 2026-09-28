from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv

# Load from the root project .env if it exists
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

class Settings(BaseSettings):
    sentinel_email: str = Field(default="", env="SENTINEL_EMAIL")
    sentinel_password: str = Field(default="", env="SENTINEL_PASSWORD")
    sentinel_camera_host: str = Field(default="103.250.160.189", env="SENTINEL_CAMERA_HOST")
    sentinel_rtsp_port: int = Field(default=8554, env="SENTINEL_RTSP_PORT")
    sentinel_hls_base: str = Field(default="https://cctv.corp8.cloud", env="SENTINEL_HLS_BASE")
    sentinel_camera_catalog: str = Field(default="https://cctv.corp8.cloud/cameras.json", env="SENTINEL_CAMERA_CATALOG")
    database_url: str = Field(default="sqlite:///./sentinel.db", env="DATABASE_URL")
    ai_processing_fps: int = Field(default=5, env="AI_PROCESSING_FPS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
