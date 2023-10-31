import psycopg2
from psycopg2.sql import SQL, Identifier
import tiktoken
import json
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel


class PostgresManager:
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
        self.conn = psycopg2.connect(url)
        self.cur = self.conn.cursor()

    def upsert(self, table_name, _dict):
        columns = _dict.keys()
        values = [SQL("%s")] * len(columns)
        upsert_stmt = SQL(
            "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT (id) DO UPDATE SET {}"
        ).format(
            Identifier(table_name),
            SQL(", ").join(map(Identifier, columns)),
            SQL(", ").join(values),
            SQL(", ").join(
                [
                    SQL("{} = EXCLUDED.{}").format(Identifier(k), Identifier(k))
                    for k in columns
                ]
            ),
        )
        self.cur.execute(upsert_stmt, list(_dict.values()))
        self.conn.commit()

    def delete(self, table_name, _id):
        delete_stmt = SQL("DELETE FROM {} WHERE id = %s").format(Identifier(table_name))
        self.cur.execute(delete_stmt, (_id,))
        self.conn.commit()

    def get(self, table_name, _id):
        select_stmt = SQL("SELECT * FROM {} WHERE id = %s").format(Identifier(table_name))
        self.cur.execute(select_stmt, (_id,))
        return self.cur.fetchone()

    def get_all(self, table_name):
        select_all_stmt = SQL("SELECT * FROM {}").format(Identifier(table_name))
        self.cur.execute(select_all_stmt)
        return self.cur.fetchall()

    def run_postgre(self, sql) -> str:
        self.cur.execute(sql)
        columns = [desc[0] for desc in self.cur.description]
        res = self.cur.fetchall()
        list_of_dicts = [dict(zip(columns, row)) for row in res]
        json_result = json.dumps(list_of_dicts, indent=4, default=self.datetime_handler)
        # dump these results to a file
        with open("results.json", "w") as f:
            f.write(json_result)
        return "Successfully delivered results to json file"

    def datetime_handler(obj):
        """
        Handle datetime objects when serializing to JSON.
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)  # or just return the object unchanged, or another default value

    def get_table_definition(self, table_name):
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
        get_all_tables_stmt = "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        self.cur.execute(get_all_tables_stmt)
        return [row[0] for row in self.cur.fetchall()]

    def get_table_definitions_for_prompt(self):
        table_names = self.get_all_table_names()
        definitions = []
        for table_name in table_names:
            definitions.append(self.get_table_definition(table_name))
        return "\n\n".join(definitions)

    def get_table_definition_map_for_embeddings(self):
        table_names = self.get_all_table_names()
        definitions = {}
        for table_name in table_names:
            definitions[table_name] = self.get_table_definition(table_name)
        return definitions


class DatabaseEmbedder:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.model = BertModel.from_pretrained("bert-base-uncased")
        self.map_name_to_embeddings = {}
        self.map_name_to_table_def = {}

    def add_table(self, table_name: str, text_representation: str):
        self.map_name_to_embeddings[table_name] = self.compute_embeddings(text_representation)
        self.map_name_to_table_def[table_name] = text_representation

    def compute_embeddings(self, text):
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
        query_embedding = self.compute_embeddings(query)
        similarities = {}
        for table_name, table_embedding in self.map_name_to_embeddings.items():
            similarities[table_name] = cosine_similarity(
                query_embedding, table_embedding
            )[0][0]
        return sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:n]
    
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
        return [self.map_name_to_table_def[table_name] for table_name in table_names]


def add_cap_ref(
    prompt: str, 
    prompt_suffix: str, 
    cap_ref: str, 
    cap_ref_content: str
) -> str:
    new_prompt = f"""{prompt} {prompt_suffix}\n{cap_ref}\n\n{cap_ref_content}"""
    return new_prompt


def count_tokens(text: str):
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def estimate_price_and_tokens(text):
    COST_PER_1k_TOKENS = 0.06
    tokens = count_tokens(text)
    estimated_cost = (tokens / 1000) * COST_PER_1k_TOKENS
    # round up to the output tokens
    estimated_cost = round(estimated_cost, 2)
    return estimated_cost, tokens

