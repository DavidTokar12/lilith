import logging
import os

from neo4j import GraphDatabase
from tqdm import tqdm

from lilith.database.utils import Neo4jDatabaseError


NEO4J_URI_VAR = "NEO4J_URI"
NEO4J_NAME_VAR = "NEO4J_NAME"
NEO4J_PASSWORD_VAR = "NEO4J_PASSWORD"


class Neo4jGraphDatabase:

    def __init__(self):
        """_summary_

        Raises:
            Neo4jDatabaseError: _description_
        """
        self.__driver = None

        self.__uri = os.environ.get(NEO4J_URI_VAR, None)
        self.__name = os.environ.get(NEO4J_NAME_VAR, None)
        self.__password = os.environ.get(NEO4J_PASSWORD_VAR, None)

        if self.__uri is None:
            raise Neo4jDatabaseError(f"{NEO4J_URI_VAR} not set.")

        if self.__name is None:
            raise Neo4jDatabaseError(f"{NEO4J_NAME_VAR} not set.")

        if self.__password is None:
            raise Neo4jDatabaseError(f"{NEO4J_PASSWORD_VAR} not set.")

    def connect(self):
        """_summary_

        Raises:
            Neo4jDatabaseError: _description_
        """
        try:
            self.__driver = GraphDatabase.driver(
                uri=self.__uri, auth=(self.__name, self.__password)
            )
            self.__driver.verify_connectivity()
        except Exception as e:
            raise Neo4jDatabaseError(f"Could not setup database connection: {e}")

    def reset_database(self) -> None:
        def delete_all_nodes(tx):
            tx.run("MATCH (n) DETACH DELETE n")

        with self.__driver.session() as session:
            session.execute_write(delete_all_nodes)

    def get_node_count(self) -> int:
        """_summary_"""

        def get_database_size(tx):
            result = tx.run("MATCH (n) RETURN count(n) AS node_count")
            node_count = result.single()["node_count"]

            return node_count

        with self.__driver.session() as session:
            node_count = session.execute_read(get_database_size)

        return node_count

    def __insert_nodes(self, node_list: list[dict]):
        def create_node(tx, node):
            query = (
                "CREATE (n:Node { id: $id, type: $type, name: $name, path: $path }) "
                "RETURN n.id AS node_id"
            )

            result = tx.run(
                query,
                id=node["id"],
                type=node["type"],
                name=node["name"],
                path=node["path"],
            )

            record = result.single()
            return record["node_id"]

        with self.__driver.session() as session:
            for node in tqdm(
                node_list,
                desc="Writing nodes to database...",
                bar_format="Lilith - INFO - {l_bar}{bar}{r_bar}",
            ):
                session.execute_write(create_node, node)

    def __create_relationships(self, node_list: list[dict]):
        def create_parent_child_relationship(tx, child_id, parent_id):
            if parent_id:
                query = (
                    "MATCH (child:Node {id: $child_id}) "
                    "WITH child "
                    "MATCH (parent:Node {id: $parent_id}) "
                    "CREATE (parent)-[:HAS_CHILD]->(child)"
                )
                tx.run(query, child_id=child_id, parent_id=parent_id)

        with self.__driver.session() as session:
            for node in tqdm(
                node_list,
                desc="Creating parent-child relationships...",
                bar_format="Lilith - INFO - {l_bar}{bar}{r_bar}",
            ):
                if node["parent"]:
                    session.execute_write(
                        create_parent_child_relationship, node["id"], node["parent"]
                    )

    def insert_data(self, node_list: list[dict]):
        """_summary_

        Args:
            node_list (list[dict]): _description_
        """
        self.__insert_nodes(node_list)
        self.__create_relationships(node_list)

    def close(self):
        self.__driver.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
