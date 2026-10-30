import os
from neo4j import GraphDatabase
import logging

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self):
        # Read from environment or fallback to docker-compose defaults
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "your-secure-password")
        self._connected = False
        self._attempted = False
        
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password),
                connection_timeout=1.0
            )
        except Exception as e:
            logger.debug(f"Failed to create Neo4j driver: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def query(self, cypher: str, parameters: dict = None):
        """
        Executes a Cypher query and returns a list of dictionaries (records).
        """
        if not self.driver:
            return []
            
        if self._attempted and not self._connected:
            return []

        try:
            with self.driver.session() as session:
                result = session.run(cypher, parameters or {})
                data = [record.data() for record in result]
                self._connected = True
                self._attempted = True
                return data
        except Exception as e:
            self._attempted = True
            self._connected = False
            logger.debug(f"Neo4j offline: {e}")
            return []
            
    def execute_write(self, cypher: str, parameters: dict = None):
        """
        Executes a write transaction in Neo4j.
        """
        if not self.driver:
            logger.warning("Neo4j driver is not initialized. Skipping write.")
            return None

        try:
            with self.driver.session() as session:
                def _write_tx(tx):
                    result = tx.run(cypher, parameters or {})
                    return [record.data() for record in result]
                return session.execute_write(_write_tx)
        except Exception as e:
            logger.error(f"Neo4j write failed: {e}")
            return None

# Singleton instance
neo4j_client = Neo4jClient()
