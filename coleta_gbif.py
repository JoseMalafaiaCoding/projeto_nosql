import requests
import csv
from time import sleep
from pathlib import Path

class GBIFCollector:
    def __init__(self, country="BR", has_coordinate=True, page_limit=300, max_records=5_000, output_file="dataset/gbif_brasil.csv"):
        self.base_url = "https://api.gbif.org/v1/occurrence/search"
        self.country = country
        self.has_coordinate = has_coordinate
        self.page_limit = page_limit  # máximo 300 por chamada
        self.max_records = max_records  # None = todos disponíveis
        self.output_file = output_file

    def get_total_count(self):
        """Obtém o total de registros disponíveis com os filtros"""
        params = {
            "country": self.country,
            "hasCoordinate": str(self.has_coordinate).lower(),
            "limit": 0
        }
        res = requests.get(self.base_url, params=params)
        res.raise_for_status()
        return res.json()["count"]

    def collect(self):
        """Faz a coleta paginada e salva em CSV"""
        if Path(self.output_file).exists():
            Path.unlink(self.output_file)
            print(f"[INFO] Arquivo {self.output_file} removido antes da coleta.")
        total = self.get_total_count()
        if self.max_records:
            total = min(total, self.max_records)
        print(f"Total de registros a coletar: {total}")

        # Definição das colunas de interesse
        fields = [
            "key",
            "datasetKey",
            "publishingOrgKey",
            "publishingCountry",
            "protocol",
            "basisOfRecord",
            "individualCount",
            "occurrenceStatus",
            "classifications",
            "taxonKey",
            "kingdomKey",
            "phylumKey",
            "classKey",
            "orderKey",
            "familyKey",
            "genusKey",
            "speciesKey",
            "scientificName",
            "scientificNameAuthorship",
            "acceptedScientificName",
            "kingdom",
            "phylum",
            "order",
            "family",
            "genus",
            "species",
            "genericName",
            "specificEpithet",
            "taxonRank",
            "taxonomicStatus",
            "decimalLatitude",
            "decimalLongitude",
            "continent",
            "stateProvince",
            "gadm",
            "year",
            "month",
            "day",
            "eventDate",
            "startDayOfYear",
            "endDayOfYear",
            "issues",
            "modified",
            "lastInterpreted",
            "references",
            "license",
            "isSequenced",
            "identifiers",
            "media",
            "facts",
            "relations",
            "isInCluster",
            "recordedBy",
            "dnaSequenceID",
            "geodeticDatum",
            "class",
            "countryCode",
            "recordedByIDs",
            "identifiedByIDs",
            "gbifRegion",
            "country",
            "publishedByGbifRegion",
            "rightsHolder",
            "identifier",
            "locality",
            "municipality",
            "fieldNumber",
            "collectionCode",
            "occurrenceID",
            "catalogNumber",
            "institutionCode",
            "ownerInstitutionCode",
            "occurrenceRemarks",
            "collectionID",
            "elevation",
            "elevationAccuracy",
            "recordNumber",
            "dateIdentified",
            "institutionKey",
            "identifiedBy",
            "lifeStage",
            "coordinateUncertaintyInMeters",
            "samplingProtocol",
            "vernacularName",
            "habitat",
            "eventTime",
            "identificationVerificationStatus",
            "eventType",
            "datasetName",
            "http://unknown.org/nick",
            "verbatimEventDate",
            "verbatimLocality",
            "taxonID",
            "http://unknown.org/captive_cultivated",
            "identificationID",
            "dynamicProperties",
            "vitality",
            "sex",
            "infraspecificEpithet",
            "reproductiveCondition",
            "informationWithheld",
            "projectId",
            "identificationRemarks"]
        with open(self.output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()

            offset = 0
            collected = 0

            while offset < total:
                params = {
                    "country": self.country,
                    "hasCoordinate": str(self.has_coordinate).lower(),
                    "limit": self.page_limit,
                    "offset": offset
                }

                res = requests.get(self.base_url, params=params)
                res.raise_for_status()
                data = res.json().get("results", [])

                for rec in data:
                    row = {field: rec.get(field, "") for field in fields}
                    writer.writerow(row)
                    collected += 1
                    if self.max_records and collected >= self.max_records:
                        print("Limite de registros atingido.")
                        return

                offset += self.page_limit
                print(f"Coletados: {collected}/{total}")
                sleep(0.2)  # pausa para não sobrecarregar a API

        print(f"Coleta finalizada. Arquivo salvo em: {self.output_file}")
