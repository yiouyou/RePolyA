from repolya._const import WORKSPACE_AUTOGEN

from repolya.autogen.organizer import AgentInstruments

import psycopg2
from psycopg2.sql import SQL, Identifier
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel
from repolya.autogen.tool_function import (
    write_file,
    write_json_file,
    write_yaml_file,
)
from dataclasses import dataclass
from datetime import datetime
import json
import os


class PostgresManager:
    """
    A class to manage postgres connections and queries
    """

    def __init__(self):
        self.conn = None
        self.cur = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def connect_with_url(self, url):
        # self.conn = psycopg2.connect(url)
        self.conn = psycopg2.connect(
            user="sz",
            password="1123",
            host=url,
            port="5432",
            database="dvdrental"
        )
        self.cur = self.conn.cursor()
    
    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def run_postgre(self, sql) -> str:
        """
        Run a SQL query against the postgres database
        """
        self.cur.execute(sql)
        columns = [desc[0] for desc in self.cur.description]
        res = self.cur.fetchall()
        list_of_dicts = [dict(zip(columns, row)) for row in res]
        json_result = json.dumps(list_of_dicts, ensure_ascii=False, indent=4, default=self.datetime_handler)
        # dump these results to a file
        with open("results.json", "w") as f:
            f.write(json_result)
        print("Successfully delivered results to json file")
        return json_result

    def datetime_handler(obj):
        """
        Handle datetime objects when serializing to JSON.
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)  # or just return the object unchanged, or another default value

    def get_table_definition(self, table_name):
        """
        Generate the 'create' definition for a table
        """
        get_def_stmt = """
        SELECT pg_class.relname as tablename,
               pg_attribute.attnum,
               pg_attribute.attname,
               format_type(atttypid, atttypmod)
        FROM pg_class
        JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
        JOIN pg_attribute ON pg_attribute.attrelid = pg_class.oid
        WHERE pg_attribute.attnum > 0
            AND pg_class.relname = %s
            AND pg_namespace.nspname = 'public'
        """
        self.cur.execute(get_def_stmt, (table_name,))
        rows = self.cur.fetchall()
        create_table_stmt = "CREATE TABLE {} (\n".format(table_name)
        for row in rows:
            create_table_stmt += "{} {},\n".format(row[2], row[3])
        create_table_stmt = create_table_stmt.rstrip(',\n') + "\n);"
        return create_table_stmt

    def get_all_table_names(self):
        """
        Get all table names in the database
        """
        get_all_tables_stmt = (
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public';"
        )
        self.cur.execute(get_all_tables_stmt)
        return [row[0] for row in self.cur.fetchall()]

    def get_table_definitions_for_prompt(self):
        """
        Get all table 'create' definitions in the database
        """
        table_names = self.get_all_table_names()
        definitions = []
        for table_name in table_names:
            definitions.append(self.get_table_definition(table_name))
        return "\n\n".join(definitions)

    def get_table_definition_map_for_embeddings(self):
        """
        Creates a map of table names to table definitions
        """
        table_names = self.get_all_table_names()
        definitions = {}
        for table_name in table_names:
            definitions[table_name] = self.get_table_definition(table_name)
        return definitions

    def get_related_tables(self, table_list, n=2):
        """
        Get tables that have foreign keys referencing the given table
        """
        related_tables_dict = {}
        for table in table_list:
            # Query to fetch tables that have foreign keys referencing the given table
            self.cur.execute(
                """
                SELECT 
                    a.relname AS table_name
                FROM 
                    pg_constraint con 
                    JOIN pg_class a ON a.oid = con.conrelid 
                WHERE 
                    confrelid = (SELECT oid FROM pg_class WHERE relname = %s)
                LIMIT %s;
                """,
                (table, n),
            )
            related_tables = [row[0] for row in self.cur.fetchall()]
            # Query to fetch tables that the given table references
            self.cur.execute(
                """
                SELECT 
                    a.relname AS referenced_table_name
                FROM 
                    pg_constraint con 
                    JOIN pg_class a ON a.oid = con.confrelid 
                WHERE 
                    conrelid = (SELECT oid FROM pg_class WHERE relname = %s)
                LIMIT %s;
                """,
                (table, n),
            )
            related_tables += [row[0] for row in self.cur.fetchall()]
            related_tables_dict[table] = related_tables
        # convert dict to list and remove dups
        related_tables_list = []
        for table, related_tables in related_tables_dict.items():
            related_tables_list += related_tables
        related_tables_list = list(set(related_tables_list))
        return related_tables_list

    # def upsert(self, table_name, _dict):
    #     columns = _dict.keys()
    #     values = [SQL("%s")] * len(columns)
    #     upsert_stmt = SQL(
    #         "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT (id) DO UPDATE SET {}"
    #     ).format(
    #         Identifier(table_name),
    #         SQL(", ").join(map(Identifier, columns)),
    #         SQL(", ").join(values),
    #         SQL(", ").join(
    #             [
    #                 SQL("{} = EXCLUDED.{}").format(Identifier(k), Identifier(k))
    #                 for k in columns
    #             ]
    #         ),
    #     )
    #     self.cur.execute(upsert_stmt, list(_dict.values()))
    #     self.conn.commit()

    # def delete(self, table_name, _id):
    #     delete_stmt = SQL("DELETE FROM {} WHERE id = %s").format(Identifier(table_name))
    #     self.cur.execute(delete_stmt, (_id,))
    #     self.conn.commit()

    # def get(self, table_name, _id):
    #     select_stmt = SQL("SELECT * FROM {} WHERE id = %s").format(Identifier(table_name))
    #     self.cur.execute(select_stmt, (_id,))
    #     return self.cur.fetchone()

    # def get_all(self, table_name):
    #     select_all_stmt = SQL("SELECT * FROM {}").format(Identifier(table_name))
    #     self.cur.execute(select_all_stmt)
    #     return self.cur.fetchall()


class DatabaseEmbedder:
    """
    This class is responsible for embedding database table definitions and
    computing similarity between user queries and table definitions.
    """

    def __init__(self, db: PostgresManager):
        self.tokenizer = BertTokenizer.from_pretrained('/home/sz/bert-base-uncased')
        self.model = BertModel.from_pretrained('/home/sz/bert-base-uncased')
        self.map_name_to_embeddings = {}
        self.map_name_to_table_def = {}
        self.db = db

    def get_similar_table_defs_for_prompt(self, prompt: str, n_similar=5, n_foreign=0):
        map_table_name_to_table_def = self.db.get_table_definition_map_for_embeddings()
        for name, table_def in map_table_name_to_table_def.items():
            self.add_table(name, table_def)
        similar_tables = self.get_similar_tables(prompt, n=n_similar)
        table_definitions = self.get_table_definitions_from_names(similar_tables)
        if n_foreign > 0:
            foreign_table_names = self.db.get_foreign_tables(similar_tables, n=3)
            table_definitions = self.get_table_definitions_from_names(
                foreign_table_names + similar_tables
            )
        return table_definitions

    def add_table(self, table_name: str, text_representation: str):
        """
        Add a table to the database embedder.
        Map the table name to its embedding and text representation.
        """
        self.map_name_to_embeddings[table_name] = self.compute_embeddings(text_representation)
        self.map_name_to_table_def[table_name] = text_representation

    def compute_embeddings(self, text):
        """
        Compute embeddings for a given text using the BERT model.
        """
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        outputs = self.model(**inputs)
        return outputs["pooler_output"].detach().numpy()

    def get_similar_tables_via_embeddings(self, query, n=3):
        """
        Given a query, find the top 'n' tables that are most similar to it.

        Args:
        - query (str): The user's natural language query.
        - n (int, optional): Number of top tables to return. Defaults to 3.

        Returns:
        - list: Top 'n' table names ranked by their similarity to the query.
        """
        # Compute the embedding for the user's query
        query_embedding = self.compute_embeddings(query)
        # Calculate cosine similarity between the query and all tables
        similarities = {
            table: cosine_similarity(query_embedding, emb)[0][0]
            for table, emb in self.map_name_to_embeddings.items()
        }
        # Rank tables based on their similarity scores and return top 'n'
        return sorted(similarities, key=similarities.get, reverse=True)[:n]
    
    def get_similar_table_names_via_word_match(self, query: str):
        """
        If any word in our query is a table name, add the table to a list
        """
        tables = []
        for table_name in self.map_name_to_table_def.keys():
            if table_name.lower() in query.lower():
                tables.append(table_name)
        return tables

    def get_similar_tables(self, query: str, n=3):
        """
        Combines results from get_similar_tables_via_embeddings and get_similar_table_names_via_word_match
        """
        similar_tables_via_embeddings = self.get_similar_tables_via_embeddings(query, n)
        similar_tables_via_word_match = self.get_similar_table_names_via_word_match(query)
        return similar_tables_via_embeddings + similar_tables_via_word_match

    def get_table_definitions_from_names(self, table_names: list) -> list:
        """
        Given a list of table names, return their table definitions.
        """
        table_defs = [
            self.map_name_to_table_def[table_name] for table_name in table_names
        ]
        return "\n\n".join(table_defs)


class PostgresAgentInstruments(AgentInstruments):
    """
    Unified Toolset for the Postgres Data Analytics Multi-Agent System
    --------------------------
    Advantages:
    - All agents have access to the same state and functions
    - Gives agent functions awareness of changing context
    - Clear and concise capabilities for agents
    - Clean database connection management
    
    Guidelines:
    - Agent Functions should not call other agent functions directly
      - Instead Agent Functions should call external lower level modules
    - Prefer 1 to 1 mapping of agents and their functions (controversial)
    - The state lifecycle lives between all agent orchestrations
    """
    
    def __init__(self, db_url: str, session_id: str) -> None:
        super().__init__()
        self.db_url = db_url
        self.db = None
        self.session_id = session_id
        self.messages = []
        self.invocation_index = 0

    def __enter__(self):
        """
        Support entering the 'with' statement
        """
        self.reset_files()
        self.db = PostgresManager()
        self.db.connect_with_url(self.db_url)
        return self, self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Support exiting the 'with' statement
        """
        self.db.close()

    def sync_messages(self, messages: list):
        """
        Syncs messages with the orchestrator
        """
        self.messages = messages

    def reset_files(self):
        """
        Clear everything in the root_dir
        """
        # if it does not exist create it
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)
        for fname in os.listdir(self.root_dir):
            os.remove(os.path.join(self.root_dir, fname))

    def get_file_path(self, fname: str):
        """
        Get the full path to a file in the root_dir
        """
        return os.path.join(self.root_dir, fname)

    # --------------------- Agent Properties --------------------- #
    @property
    def run_postgre_results_file(self):
        return self.get_file_path("run_postgre_results.json")
    
    @property
    def postgre_query_file(self):
        return self.get_file_path("postgre_query.sql")

    # --------------------- Agent Functions --------------------- #
    def run_postgre(self, sql: str) -> str:
        """
        Run a SQL query against the postgres database
        """
        results_as_json = self.db.run_postgre(sql)
        fname = self.run_postgre_results_file
        # dump these results to a file
        with open(fname, "w") as f:
            f.write(results_as_json)
        with open(self.postgre_query_file, "w") as f:
            f.write(sql)
        return "Successfully delivered results to json file"

    def validate_run_postgre(self):
        """
        Validate that the run_sql results file exists and has content
        """
        fname = self.run_postgre_results_file
        with open(fname, "r") as f:
            content = f.read()
        if not content:
            return False, f"File {fname} is empty"
        return True, ""

    def write_file(self, content: str):
        fname = self.get_file_path("write_file.txt")
        return write_file(fname, content)

    def write_json_file(self, json_str: str):
        fname = self.get_file_path("write_json_file.json")
        return write_json_file(fname, json_str)

    def write_yaml_file(self, yaml_str: str):
        fname = self.get_file_path("write_yaml_file.yml")
        return write_yaml_file(fname, yaml_str)

    def write_innovation_file(self, content: str):
        fname = self.get_file_path(f"{self.innovation_index}_innovation_file.txt")
        write_file(fname, content)
        self.innovation_index += 1
        return "Successfully wrote innovation file. You can check my work."

    def validate_innovation_files(self):
        """
        Loop from 0 to innovation_index and verify file exists with content
        """
        for i in range(self.innovation_index):
            fname = self.get_file_path(f"{i}_innovation_file.txt")
            with open(fname, "r") as f:
                content = f.read()
                if not content:
                    return False, f"File {fname} is empty"
        return True, ""

