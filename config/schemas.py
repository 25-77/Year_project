from pydantic import BaseModel
from pathlib import Path


class ClickHouseCredentials(BaseModel):
    username: str
    password: str
    ssh_pkey: str | Path

class PostgreCredentials(BaseModel):
    username: str
    password: str


class Settings(BaseModel):
    clickhouse_creds: ClickHouseCredentials
    postgre_creds: PostgreCredentials