import os


class Config:
    DB_CONFIG = os.getenv(
        "DB_CONFIG",
        "postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}".format(
            DB_USER=os.getenv("DB_USER", "fastapi"),
            DB_PASSWORD=os.getenv("DB_PASSWORD", "fastapi-password"),
            DB_HOST=os.getenv("DB_HOST", "fastapi-postgresql:5432"),
            DB_NAME=os.getenv("DB_NAME", "fastapi"),
        ),
    )

    MODELS_BASE_DIR = os.getenv("MODELS_BASE_DIR", "/var/lib/edaparts/library")


config = Config
