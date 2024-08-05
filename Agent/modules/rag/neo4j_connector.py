import pandas as pd
from neo4j import GraphDatabase

from utils.get_logger import get_logger

logger = get_logger(__name__)


class Neo4jConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_cypher_query(self, query) -> pd.DataFrame:
        with self.driver.session() as session:
            result = session.run(query)

            records = list(result)
            total_records = len(records)
            logger.debug(f"Total records: {total_records}")
        df = pd.DataFrame([dict(r) for r in records])
        return df


if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "testpassword"

    neo4j_connector = Neo4jConnector(uri, username, password)
    query = """
    MATCH (n)
    WHERE n.content_embedding IS NULL
    RETURN n
    """
    result = neo4j_connector.run_cypher_query(query)
    logger.info(result)
    neo4j_connector.close()
