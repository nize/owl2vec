# requirements.txt
# -----------------
# qdrant-client
# openai
# SPARQLWrapper
# tqdm

import os
import uuid
from openai import OpenAI
from qdrant_client import QdrantClient, models
from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---

# GraphDB configuration
GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/kg-llm"

# Qdrant configuration
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION_NAME = "fibo_knowledge_graph"

# OpenAI configuration
# Make sure you have the OPENAI_API_KEY environment variable set
# You can get your key from https://platform.openai.com/account/api-keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# Choose your desired embedding model: "text-embedding-3-small" or "text-embedding-3-large"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"

# The embedding dimension depends on the model
EMBEDDING_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072
}
VECTOR_SIZE = EMBEDDING_DIMENSIONS.get(OPENAI_EMBEDDING_MODEL)

# Set to None to index all items, or an integer to limit the number of items for testing.
MAX_ITEMS_TO_INDEX = 100 # or None to index everything

# --- Main Script ---

def get_graph_data(endpoint_url):
    """
    Queries the GraphDB SPARQL endpoint to retrieve entities and their textual descriptions.
    """
    print("Querying GraphDB to retrieve data...")
    sparql = SPARQLWrapper(endpoint_url)
    # This query retrieves classes and various textual annotations.
    # It groups results by URI to concatenate multiple synonyms and explanatory notes.
    sparql.setQuery("""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX cmns-av: <https://www.omg.org/spec/Commons/AnnotationVocabulary/>

        SELECT ?uri 
               (SAMPLE(?label) as ?sampleLabel)
               (SAMPLE(?prefLabel) as ?samplePrefLabel)
               (SAMPLE(?definition) as ?sampleDefinition)
               (SAMPLE(?example) as ?sampleExample)
               (GROUP_CONCAT(DISTINCT ?synonym; SEPARATOR=" | ") as ?synonyms)
               (GROUP_CONCAT(DISTINCT ?explanatoryNote; SEPARATOR=" | ") as ?explanatoryNotes)
        WHERE {
          ?uri a owl:Class .
          FILTER(isIRI(?uri))
          
          OPTIONAL { ?uri rdfs:label ?label . }
          OPTIONAL { ?uri skos:prefLabel ?prefLabel . }
          OPTIONAL { ?uri skos:definition ?definition . }
          OPTIONAL { ?uri skos:example ?example . }
          OPTIONAL { ?uri cmns-av:synonym ?synonym . }
          OPTIONAL { ?uri cmns-av:explanatoryNote ?explanatoryNote . }
        }
        GROUP BY ?uri
    """)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        print(f"Successfully retrieved {len(results['results']['bindings'])} entities from GraphDB.")
        return results["results"]["bindings"]
    except Exception as e:
        print(f"Error querying GraphDB: {e}")
        return []

def create_embeddings(text, client):
    """
    Generates embeddings for the given text using the OpenAI API.
    """
    try:
        response = client.embeddings.create(
            input=text,
            model=OPENAI_EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error creating embedding for text '{text[:50]}...': {e}")
        return None


def index_data(data, qdrant_client, openai_client):
    """
    Generates embeddings and indexes the data into Qdrant.
    """
    print(f"Indexing data into Qdrant collection '{QDRANT_COLLECTION_NAME}'...")
    points_to_upsert = []
    for item in tqdm(data, desc="Processing entities"):
        uri = item.get("uri", {}).get("value")
        if not uri:
            continue

        # Extract data from the query results
        label = item.get("sampleLabel", {}).get("value", "")
        pref_label = item.get("samplePrefLabel", {}).get("value", "")
        definition = item.get("sampleDefinition", {}).get("value", "")
        example = item.get("sampleExample", {}).get("value", "")
        synonyms = item.get("synonyms", {}).get("value", "")
        explanatory_notes = item.get("explanatoryNotes", {}).get("value", "")
        
        # We create a single, rich text entry for embedding
        text_to_embed = (
            f"Label: {label}\n"
            f"Preferred Label: {pref_label}\n"
            f"Definition: {definition}\n"
            f"Synonyms: {synonyms}\n"
            f"Explanatory Notes: {explanatory_notes}\n"
            f"Example: {example}"
        ).strip()
        
        if not text_to_embed:
            continue

        # Create embedding for the text
        vector = create_embeddings(text_to_embed, openai_client)

        if vector:
            points_to_upsert.append(
                models.PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_URL, uri)),
                    vector=vector,
                    payload={
                        "uri": uri,
                        "text": text_to_embed,
                        "label": label,
                        "pref_label": pref_label,
                        "definition": definition,
                        "synonyms": synonyms,
                        "explanatory_notes": explanatory_notes,
                        "example": example,
                    }
                )
            )
        
        # Upsert in batches to avoid overwhelming the server
        if len(points_to_upsert) >= 100:
            qdrant_client.upsert(
                collection_name=QDRANT_COLLECTION_NAME,
                points=points_to_upsert,
                wait=True
            )
            points_to_upsert = []

    # Upsert any remaining points
    if points_to_upsert:
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points_to_upsert,
            wait=True
        )

    print("Data indexing complete.")


if __name__ == "__main__":
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable not set.")
        exit(1)

    if not VECTOR_SIZE:
        print(f"Error: Invalid OpenAI model name '{OPENAI_EMBEDDING_MODEL}'.")
        exit(1)

    # Initialize clients
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    qdrant_client = QdrantClient(url=QDRANT_URL)

    # Create Qdrant collection if it doesn't exist
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        if QDRANT_COLLECTION_NAME not in collection_names:
            print(f"Creating Qdrant collection: {QDRANT_COLLECTION_NAME}")
            qdrant_client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
            )
        else:
            print(f"Using existing Qdrant collection: {QDRANT_COLLECTION_NAME}")

    except Exception as e:
        print(f"Error connecting to or setting up Qdrant: {e}")
        exit(1)


    # Get data from GraphDB
    graph_data = get_graph_data(GRAPHDB_ENDPOINT)

    if graph_data:
        # Limit the number of items to index if configured
        if MAX_ITEMS_TO_INDEX is not None and isinstance(MAX_ITEMS_TO_INDEX, int):
            print(f"Limiting indexing to the first {MAX_ITEMS_TO_INDEX} items.")
            graph_data = graph_data[:MAX_ITEMS_TO_INDEX]
            
        # Index the data
        index_data(graph_data, qdrant_client, openai_client)
