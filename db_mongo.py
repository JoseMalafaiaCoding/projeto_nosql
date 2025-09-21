import pandas as pd
from pymongo import MongoClient

class MongoFactIngestorFromCSV:
    def __init__(self, csv_file, mongo_uri, mongo_db, mongo_collection):
        self.csv_file = csv_file
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.client = None
        self.mongo = None

        # Campos que serão extraídos do CSV
        self.fields = [
            "kingdomKey", "phylumKey", "classKey", "orderKey",
            "familyKey", "genusKey", "speciesKey",
            "scientificName", "scientificNameAuthorship",
            "decimalLatitude", "decimalLongitude",
            "continent", "stateProvince", "gadm",
            "year", "month", "day", "eventDate",
            "media", "recordedBy", "country", "locality",
            "municipality", "identifiedBy", "eventTime",
            "eventType", "sex", "habitat"
        ]

    def connect(self):
        """Conecta ao MongoDB"""
        self.client = MongoClient(self.mongo_uri)
        self.mongo = self.client[self.mongo_db][self.mongo_collection]
        print(f"Conectado ao MongoDB: {self.mongo_db}.{self.mongo_collection}")

    def read_csv(self):
        """Lê os dados do CSV"""
        print("Lendo CSV...")
        df = pd.read_csv(self.csv_file, low_memory=False)
        df = df[[c for c in self.fields if c in df.columns]]
        print(f"Total de registros lidos: {len(df)}")
        return df

    def transform_records(self, df):
        """Transforma registros em dicionários com coordenadas"""
        records = []
        for _, row in df.iterrows():
            doc = row.to_dict()

            # Extrair coordenadas
            lat = doc.pop("decimalLatitude", None)
            lon = doc.pop("decimalLongitude", None)
            doc["coordenadas"] = {
                "decimalLatitude": lat,
                "decimalLongitude": lon
            }

            records.append(doc)
        return records

    def insert_to_mongo(self, records):
        """Insere registros no MongoDB"""
        self.mongo.drop()
        if records:
            self.mongo.insert_many(records)
            print(f"{len(records)} registros inseridos no MongoDB.")

    def run(self):
        """Executa todo o fluxo"""
        self.connect()
        df = self.read_csv()
        records = self.transform_records(df)
        self.insert_to_mongo(records)