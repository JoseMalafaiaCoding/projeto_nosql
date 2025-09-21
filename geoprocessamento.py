from pymongo import MongoClient
from geopy.distance import geodesic
import folium

class GeoProcessor:
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.client = None
        self.collection = None

    def connect(self):
        """Conecta ao MongoDB"""
        self.client = MongoClient(self.mongo_uri)
        self.collection = self.client[self.mongo_db][self.mongo_collection]

    def get_nearest_points(self, latitude, longitude, n=3):
        """Retorna os N pontos mais próximos do ponto informado"""
        if self.collection is None:
            raise Exception("Conecte ao MongoDB primeiro com connect()")

        # Busca apenas docs que possuem coordenadas válidas
        docs = self.collection.find(
            {"coordenadas.decimalLatitude": {"$ne": None},
             "coordenadas.decimalLongitude": {"$ne": None}},
            {"coordenadas.decimalLatitude": 1, 
             "coordenadas.decimalLongitude": 1, 
             "scientificName": 1,
             "kingdomKey": 1,
             "phylumKey": 1,
             "classKey": 1,
             "orderKey": 1,
             "familyKey": 1,
             "genusKey": 1,
             "speciesKey": 1}
        )

        base_point = (latitude, longitude)
        distances = []

        for doc in docs:
            lat = doc["coordenadas"]["decimalLatitude"]
            lon = doc["coordenadas"]["decimalLongitude"]
            if lat is not None and lon is not None:
                point = (lat, lon)
                dist = geodesic(base_point, point).kilometers
                distances.append({
                    "scientificName": doc.get("scientificName"),
                    "latitude": lat,
                    "longitude": lon,
                    "distance_km": dist,
                    "kingdomKey": doc.get("kingdomKey"),
                    "phylumKey": doc.get("phylumKey"),
                    "classKey": doc.get("classKey"),
                    "orderKey": doc.get("orderKey"),
                    "familyKey": doc.get("familyKey"),
                    "genusKey": doc.get("genusKey"),
                    "speciesKey": doc.get("speciesKey")
                })

        # Ordena pela menor distância
        distances = sorted(distances, key=lambda x: x["distance_km"])
        return distances[:n]