# requirements.txt
# -----------------
# qdrant-client
# openai
# SPARQLWrapper
# tqdm

import os
import uuid
from datetime import datetime
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
QDRANT_COLLECTION_NAME = "acme_knowledge_graph"

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
MAX_ITEMS_TO_INDEX = 20 # or None to index everything

# --- Main Script ---

def get_graph_data(endpoint_url):
    """
    Queries the GraphDB SPARQL endpoint to retrieve entities and their textual descriptions.
    """
    print("Querying GraphDB to retrieve data...")
    sparql = SPARQLWrapper(endpoint_url)
    # This query retrieves classes and all their annotation properties and built-in properties,
    # excluding specific properties that are not relevant for embeddings.
    sparql.setQuery("""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX cmns-av: <https://www.omg.org/spec/Commons/AnnotationVocabulary/>
        PREFIX sm: <http://www.omg.org/techprocess/ab/SpecificationMetadata/>

        SELECT ?uri ?property ?value ?entityType
        FROM <http://acme.com/graph/fibo-ontology>
        FROM <http://acme.com/graph/acme-ontology>
        WHERE {
          # Match entities of different types
          {
            ?uri a owl:Class .
            BIND("Class" AS ?entityType)
          }
          UNION
          {
            ?uri a owl:NamedIndividual .
            BIND("NamedIndividual" AS ?entityType)
          }
          UNION
          {
            ?uri a owl:ObjectProperty .
            BIND("ObjectProperty" AS ?entityType)
          }
          UNION
          {
            ?uri a owl:DatatypeProperty .
            BIND("DatatypeProperty" AS ?entityType)
          }
          
          FILTER(isIRI(?uri))
          
          ?uri ?property ?value .
          
          # Include annotation properties OR built-in properties
          {
            ?property a owl:AnnotationProperty .
          }
          UNION
          {
            FILTER(?property IN (
              rdfs:label,
              rdfs:comment,
              rdfs:seeAlso,
              rdfs:isDefinedBy,
              owl:versionInfo
            ))
          }
          
          # Exclude specific properties (not adding direct meaning)
          FILTER(?property NOT IN (
            dct:issued,
            dct:license,
            dct:modified,
            cmns-av:copyright,
            cmns-av:adaptedFrom
            dct:rights,
            sm:directSource,
            owl:minQualifiedCardinality,
            dct:source,
            owl:versionInfo
          ))
          
          # Only include literal values (text)
          FILTER(isLiteral(?value))
        }
    """)
    
    # Disable inference to avoid duplicated content from reasoner
    sparql.addParameter("infer", "false")
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        print(f"Successfully retrieved {len(results['results']['bindings'])} property-value pairs from GraphDB.")
        
        # Group the results by URI
        grouped_data = {}
        for binding in results['results']['bindings']:
            uri = binding.get("uri", {}).get("value")
            property_uri = binding.get("property", {}).get("value")
            value = binding.get("value", {}).get("value")
            entity_type = binding.get("entityType", {}).get("value")
            
            if not uri or not property_uri or not value or not entity_type:
                continue
                
            if uri not in grouped_data:
                grouped_data[uri] = {
                    "properties": {},
                    "entity_types": set()
                }
                
            # Track entity types (using set to handle punning automatically)
            grouped_data[uri]["entity_types"].add(entity_type)
                
            # Extract the property name from the URI (everything after the last # or /)
            property_name = property_uri.split('#')[-1] if '#' in property_uri else property_uri.split('/')[-1]
            
            if property_name not in grouped_data[uri]["properties"]:
                grouped_data[uri]["properties"][property_name] = set()  # Use set to avoid duplicates
                
            grouped_data[uri]["properties"][property_name].add(value)
        
        # Convert grouped data back to the expected format
        processed_data = []
        for uri, data in grouped_data.items():
            # Convert sets to lists for properties, removing duplicates
            properties_dict = {}
            for prop_name, value_set in data["properties"].items():
                properties_dict[prop_name] = list(value_set)  # Convert set to list
            
            processed_data.append({
                "uri": {"value": uri},
                "properties": properties_dict,
                "entity_types": list(data["entity_types"])  # Convert set to list
            })
            
        print(f"Processed into {len(processed_data)} unique entities.")
        return processed_data
        
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
    Only creates new embeddings if the text content has changed.
    """
    print(f"Indexing data into Qdrant collection '{QDRANT_COLLECTION_NAME}'...")
    
    # Get existing points to check for changes
    print("Checking existing points for changes...")
    existing_points = {}
    try:
        # Retrieve all existing points (in batches if needed)
        scroll_result = qdrant_client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            limit=10000,  # Adjust based on your collection size
            with_payload=True,
            with_vectors=False  # We don't need the vectors, just the payload
        )
        for point in scroll_result[0]:
            if point.payload and 'uri' in point.payload:
                existing_points[point.payload['uri']] = point.payload.get('text', '')
        
        print(f"Found {len(existing_points)} existing points.")
    except Exception as e:
        print(f"Warning: Could not retrieve existing points: {e}")
        print("Proceeding without change detection...")
    
    points_to_upsert = []
    skipped_count = 0
    updated_count = 0
    
    for item in tqdm(data, desc="Processing entities"):
        uri = item.get("uri", {}).get("value")
        if not uri:
            continue

        # Extract all properties and entity types
        properties = item.get("properties", {})
        entity_types = item.get("entity_types", [])
        
        # Build the text to embed from all properties
        text_parts = []
        for property_name, values in properties.items():
            if values:  # Only include if there are values
                # Join multiple values with " | " separator
                combined_values = " | ".join(values)
                # Make property names stand out with brackets and uppercase
                text_parts.append(f"[{property_name.upper()}]: {combined_values}")
        
        text_to_embed = "\n".join(text_parts).strip()
        
        if not text_to_embed:
            continue

        # Check if text has changed compared to existing point
        existing_text = existing_points.get(uri, None)
        if existing_text == text_to_embed:
            skipped_count += 1
            continue  # Skip if text hasn't changed
        
        # Create embedding for the text (only if changed or new)
        vector = create_embeddings(text_to_embed, openai_client)

        if vector:
            # Add current timestamp
            current_time = datetime.now().isoformat()
            
            points_to_upsert.append(
                models.PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_URL, uri)),
                    vector=vector,
                    payload={
                        "uri": uri,
                        "text": text_to_embed,
                        "entity_type": entity_types,
                        "last_updated": current_time,
                    }
                )
            )
            updated_count += 1
        
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

    print(f"Data indexing complete. Updated: {updated_count}, Skipped (unchanged): {skipped_count}")


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
