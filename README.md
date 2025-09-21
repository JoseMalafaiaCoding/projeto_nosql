# 🌱 Projeto GBIF Brasil – Coleta, Armazenamento e Visualização de Ocorrências Biodiversidade

Este projeto realiza a **coleta de dados ambientais do GBIF (Global Biodiversity Information Facility)** para o Brasil, armazena-os em bancos de dados relacionais (**SQLite**) e não relacionais (**MongoDB**) e oferece uma interface interativa com **Streamlit**, incluindo funcionalidades de **geoprocessamento** e **visualização em mapas interativos**.

---

## ✨ Funcionalidades Implementadas

1. **Coleta de dados do GBIF**

   * Utiliza a API do GBIF para coletar registros de ocorrência de espécies no Brasil.
   * Filtros aplicados: `hasCoordinates=True` e `country="BR"`.
   * Dados são coletados de forma **paginada** respeitando o limite da API.
   * Os registros são salvos em **CSV** (sobrescrevendo caso já exista).

2. **Banco de Dados Relacional (SQLite)**

   * Criação automática do banco em uma pasta `database/`.
   * Criação de tabelas dimensionais para classificações taxonômicas:

     * `dim_kingdom`, `dim_phylum`, `dim_class`, `dim_order`, `dim_family`, `dim_genus`, `dim_species`.
   * Cada dimensão contém a chave (`*_Key`) e o nome (`*_Name`) correspondente.

3. **Banco de Dados Não Relacional (MongoDB)**

   * Conexão via **connection string**.
   * Criação automática de **database** e **collection**.
   * Ingestão da tabela fato `occurrences` com os seguintes campos:

     * `kingdomKey, phylumKey, classKey, orderKey, familyKey, genusKey, speciesKey`
     * `scientificName, scientificNameAuthorship`
     * `decimalLatitude, decimalLongitude` → armazenados no BSON dentro de `coordenadas`.
     * `continent, stateProvince, gadm, year, month, day, eventDate, media, recordedBy, country, locality, municipality, identifiedBy, eventTime, eventType, sex, habitat`.

4. **Relacionamento MongoDB ↔ SQLite**

   * As tabelas fato do MongoDB podem ser enriquecidas com informações taxonômicas armazenadas no SQLite.

5. **Geoprocessamento**

   * Utiliza **geopy** para calcular distâncias.
   * Dada uma coordenada (`latitude`, `longitude`), retorna os **3 pontos mais próximos** da base de dados.
   * Visualização dos pontos no **mapa interativo com Folium**.
   * Possibilidade de selecionar pontos clicando diretamente no mapa.

6. **Interface Interativa (Streamlit)**

   * Exibe o mapa interativo.
   * Ao clicar em um ponto, são exibidas as **3 ocorrências mais próximas**.
   * As informações taxonômicas correspondentes (reino, filo, família, etc.) são carregadas do SQLite e mostradas ao lado das ocorrências.
   * O mapa é atualizado dinamicamente conforme o usuário interage.

---

## 🛠️ Pré-requisitos

* **Python 3.9+**
* **MongoDB** em execução local ou remoto (Atlas, Docker, etc.)
* **SQLite** (já embutido no Python)

---

## 📦 Instalação

Clone o repositório e entre na pasta do projeto:

```bash
git clone https://github.com/seuusuario/projeto-gbif-brasil.git
cd projeto-gbif-brasil
```

Execute o arquivo run_app.bat
---

## ▶️ Execução do Projeto

1. **Ingestão de dados**

   * A primeira execução já faz a coleta dos dados do GBIF e a ingestão nos bancos (SQLite e MongoDB).
   * Os arquivos e bancos são sobrescritos automaticamente para manter a consistência.

2. **Rodar a interface**

   ```bash
   streamlit run main.py
   ```

3. **Acessar a aplicação**

   * Abra o navegador em: [http://localhost:8501](http://localhost:8501)

---

## 📂 Estrutura do Projeto

```
projeto-gbif-brasil/
│── main.py                 # Aplicação Streamlit
│── gbif_collector.py       # Classe para coletar dados do GBIF
│── sqlite_manager.py       # Classe para criação das dimensões no SQLite
│── mongodb_manager.py      # Classe para ingestão no MongoDB
│── geo_processor.py        # Classe para geoprocessamento com geopy/folium
│── integrator.py           # Classe para integrar MongoDB e SQLite
│── requirements.txt        # Dependências do projeto
│── README.md               # Documentação do projeto
│── database/               # Banco SQLite criado automaticamente
│── data/                   # CSVs baixados do GBIF
```

---

## 🗺️ Demonstração da Interface

* **Mapa interativo com pontos de ocorrência**
* **Clique em qualquer lugar para obter as 3 ocorrências mais próximas**
* **Exibição de informações taxonômicas detalhadas ao lado**

---

## ⚠️ Observações Importantes

* O volume total de registros do GBIF pode ultrapassar **30 milhões**, o que gera muitos GBs de dados. Para testes locais, recomenda-se coletar apenas uma amostra (usando filtros adicionais, como `year`, `taxonKey`, ou limitar páginas).
* O MongoDB precisa estar em execução antes de rodar o projeto.
* O SQLite será criado automaticamente em `database/gbif.db`.

---

👉 Quer que eu adapte este `README.md` para ficar pronto para publicar no **GitHub**, com badges (Python, MongoDB, Streamlit) e prints da interface?
