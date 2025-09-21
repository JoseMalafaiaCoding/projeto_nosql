import sqlite3
import pandas as pd
import os

class TaxonomyLoader:
    def __init__(self, csv_file, db_file="database/taxonomy.db"):
        self.csv_file = csv_file
        self.db_file = db_file
        self.conn = None

    def create_database(self):
        """Cria o banco de dados SQLite do zero"""
        if self.conn:
            self.conn.close()

        if os.path.exists(self.db_file):
            print(f"Banco de dados ja existe '{self.db_file}'")
            return

        self.conn = sqlite3.connect(self.db_file)
        print(f"Novo banco de dados '{self.db_file}' criado.")

    def load_csv(self):
        """Carrega o CSV do GBIF em DataFrame"""
        print("Lendo CSV...")
        self.df = pd.read_csv(self.csv_file, low_memory=False)
        print(f"Total de registros lidos: {len(self.df)}")

    def create_tables(self):
        """Cria tabelas dimensão no SQLite"""
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()

        dims = {
            "kingdom": ("kingdomKey", "kingdom"),
            "phylum": ("phylumKey", "phylum"),
            "class": ("classKey", "class"),
            "order": ("orderKey", "order"),
            "family": ("familyKey", "family"),
            "genus": ("genusKey", "genus"),
            "species": ("speciesKey", "species")
        }

        for dim, (key_col, name_col) in dims.items():
            table_name = f"dim_{dim}"
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            cursor.execute(f"""
                    CREATE TABLE `{table_name}` (
                    `{key_col}` INTEGER PRIMARY KEY,
                    `{name_col}` TEXT
                )
            """)
        self.conn.commit()
        print("Tabelas de dimensões criadas.")

    def populate_dimensions(self):
        """Popula as tabelas de dimensões com dados únicos do CSV"""
        dims = {
            "kingdom": ("kingdomKey", "kingdom"),
            "phylum": ("phylumKey", "phylum"),
            "class": ("classKey", "class"),
            "order": ("orderKey", "order"),
            "family": ("familyKey", "family"),
            "genus": ("genusKey", "genus"),
            "species": ("speciesKey", "species")
        }

        for dim, (key_col, name_col) in dims.items():
            table_name = f"dim_{dim}"
            subset = self.df[[key_col, name_col]].dropna().drop_duplicates()
            subset.to_sql(table_name, self.conn, if_exists="append", index=False)
            print(f"Tabela {table_name} populada com {len(subset)} registros únicos.")

    
    def load_taxonomy(self, sqlite_path="database/taxonomy.db"):
        """
        Carrega as dimensões taxonômicas do SQLite e devolve como dicionários
        para lookup pelo *_Key.
        """
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()

        taxonomy = {}
        dims = ["kingdom", "phylum", "class", "order", "family", "genus", "species"]

        for dim in dims:
            table = f"dim_{dim}"
            cur.execute(f"SELECT `{dim}Key`, `{dim}` FROM `{table}`")
            taxonomy[dim] = {row[0]: row[1] for row in cur.fetchall()}

        conn.close()
        return taxonomy

    def close(self):
        self.conn.close()
        print("Conexão com o banco fechada.")