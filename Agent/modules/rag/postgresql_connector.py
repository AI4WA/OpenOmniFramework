import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from utils.get_logger import get_logger

logger = get_logger(__name__)


class PostgresqlConnector:
    def __init__(self, database: str, user: str, password: str, host: str, port: str):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.engine = self.create_engine()

    def create_engine(self) -> Engine:
        connection_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        engine = create_engine(connection_string)
        return engine

    def execute(self, query: str) -> pd.DataFrame:
        with self.engine.connect() as connection:
            result_df = pd.read_sql(query, connection)
        return result_df


if __name__ == "__main__":
    # Example usage
    pg = PostgresqlConnector(
        database="yourdbname",
        user="youruser",
        password="yourpassword",
        host="localhost",
        port="5432",
    )
    query = "SELECT * FROM orchestrator_task"
    result = pg.execute(query)
