import streamlit as st
from streamlit_folium import st_folium
import folium
from geoprocessamento import *
from db_sqlite import *
from db_mongo import *
from pathlib import Path
from coleta_gbif import *
from bs4 import BeautifulSoup

# Configuração do Mongo
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "gbif"
COLLECTION = "occurrences"
CSV_FILE = "dataset/gbif_brasil.csv"

@st.cache_data(show_spinner="Carregando dados do GBIF, aguarde...")
def ingest_data():
    Path("database").mkdir(exist_ok=True)
    Path("dataset").mkdir(exist_ok=True)
    
    gbif_collector = GBIFCollector()
    sqlite = TaxonomyLoader(csv_file=CSV_FILE)
    mongo = MongoFactIngestorFromCSV(
        csv_file=CSV_FILE, 
        mongo_uri=MONGO_URI, 
        mongo_db=DB_NAME, 
        mongo_collection=COLLECTION)
    
    gbif_collector.collect()
    sqlite.create_database()
    sqlite.load_csv()
    sqlite.create_tables()
    sqlite.populate_dimensions()
    mongo.connect()
    df = mongo.read_csv()
    records = mongo.transform_records(df)
    mongo.insert_to_mongo(records)
ingest_data()
taxonomy = TaxonomyLoader(CSV_FILE).load_taxonomy()
geo = GeoProcessor(MONGO_URI, DB_NAME, COLLECTION)
geo.connect()

st.set_page_config(page_title="GeoProcessamento GBIF", layout="wide")

st.title("🌍 GeoProcessamento de Ocorrências (GBIF)")

# Estado para armazenar coordenadas clicadas
if "click_coords" not in st.session_state:
    st.session_state.click_coords = None
if "nearest_points" not in st.session_state:
    st.session_state.nearest_points = []

if "zoom" not in st.session_state:
    st.session_state.zoom = 4
if "map_center" not in st.session_state:
    st.session_state.map_center = [-14.2350, -51.9253]  # Brasil

# Criar mapa com valores da sessão
m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.zoom)

if st.session_state.click_coords:
    lat, lon = st.session_state.click_coords

    # Ponto clicado
    folium.Marker(
        [lat, lon],
        popup="Ponto selecionado",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    # Ocorrências mais próximas
    for p in st.session_state.nearest_points:
        folium.Marker(
            [p["latitude"], p["longitude"]],
            popup=f"{p['scientificName']} - {p['distance_km']:.2f} km",
            icon=folium.Icon(color="blue", icon="leaf")
        ).add_to(m)

map_data = st_folium(m, width=800, height=600)

if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    # Atualiza estado
    st.session_state.click_coords = (lat, lon)
    st.session_state.nearest_points = geo.get_nearest_points(lat, lon, n=3)
    st.session_state.map_center = [lat, lon]
    st.rerun()
# Mostrar lista de ocorrências mais próximas
if st.session_state.nearest_points:
    st.subheader("🔎 Ocorrências mais próximas")
    for p in st.session_state.nearest_points:
        st.write(
            f"""**{p['scientificName']}** — 📍 ({p['latitude']}, {p['longitude']}) — 
            Distância: {p['distance_km']:.2f} km\n
            Reino: {taxonomy['kingdom'].get(p['kingdomKey'])}\n
            Filo: {taxonomy['phylum'].get(p['phylumKey'])}\n
            Classe: {taxonomy['class'].get(p['classKey'])}\n
            Ordem: {taxonomy['order'].get(p['orderKey'])}\n
            Família: {taxonomy['family'].get(p['familyKey'])}\n
            Gênero: {taxonomy['genus'].get(p['genusKey'])}\n
            Espécie: {taxonomy['species'].get(p['speciesKey'])}""")
        if not p["references"] or not p["format"]:
            st.warning("Nenhuma referência de imagem disponível para esta ocorrência.")
        elif p["format"] not in ["image/jpeg", "image/png"]:
            st.info(f"Formato não suportado: {p['format']}")
        
        else:
            url = p["references"]
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                # Pega a imagem principal do meta og:image
                og_img = soup.find("meta", property="og:image")
                if og_img:
                    st.image(og_img["content"], caption="Imagem principal")

            except Exception as e:
                st.error(f"Erro ao carregar imagens da referência: {e}")