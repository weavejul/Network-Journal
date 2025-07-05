"""
Neo4j database connection management.
"""

import sys
from pathlib import Path
from typing import Optional, Generator
from contextlib import contextmanager

# Add the shared package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from neo4j import GraphDatabase, Driver, Session
from shared.config import get_settings
from shared.utils import setup_logging

logger = setup_logging(__name__)
settings = get_settings()


class Neo4jConnection:
    """Neo4j database connection manager."""
    
    def __init__(self):
        self._driver: Optional[Driver] = None
    
    def connect(self) -> Driver:
        """Create and return a Neo4j driver instance."""
        if self._driver is None:
            try:
                self._driver = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
                )
                # Test the connection
                with self._driver.session(database=settings.NEO4J_DATABASE) as session:
                    session.run("RETURN 1")
                logger.info(f"Connected to Neo4j at {settings.NEO4J_URI}")
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {e}")
                raise
        return self._driver
    
    def close(self):
        """Close the Neo4j driver connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")
    
    @contextmanager
    def get_session(self, database: Optional[str] = None) -> Generator[Session, None, None]:
        """Get a Neo4j session with automatic cleanup."""
        driver = self.connect()
        session = driver.session(database=database or settings.NEO4J_DATABASE)
        try:
            yield session
        finally:
            session.close()


# Global connection instance
neo4j_connection = Neo4jConnection()


def get_neo4j_session(database: Optional[str] = None) -> Session:
    """Get a Neo4j session for database operations."""
    return neo4j_connection.get_session(database)


@contextmanager
def get_session_context(database: Optional[str] = None) -> Generator[Session, None, None]:
    """Context manager for Neo4j sessions."""
    with neo4j_connection.get_session(database) as session:
        yield session 