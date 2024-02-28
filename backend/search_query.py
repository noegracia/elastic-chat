from dotenv import load_dotenv
import os
from elasticsearch import Elasticsearch

# Load environment variables from .env file
load_dotenv("../.env")


# Code based on:
# https://www.elastic.co/blog/chatgpt-elasticsearch-openai-meets-private-data

# Required Environment Variables
cloud_id = os.getenv('ELASTIC_CLOUD_ID')
cloud_user = os.getenv('ELASTIC_USERNAME')
cloud_pass = os.getenv('ELASTIC_PASSWORD')

# Connect to Elastic Cloud cluster
def es_connect(cloud_id, user, passwd):
    es = Elasticsearch(cloud_id=cloud_id, http_auth=(user, passwd))
    return es

# Search ElasticSearch index and return body and URL of the result
def search(query_text):
    es = es_connect(cloud_id, cloud_user, cloud_pass)

    # Elasticsearch query (BM25) and kNN configuration for hybrid search
    body = {
        "query": {
            "bool": {
                "should": [{
                    "match": {
                        "title": {
                            "query": query_text,
                            "boost": 1
                        }
                    }
                }],
                "filter": [{
                    "exists": {
                        "field": "ml.inference.body_content.predicted_value"
                    }
                }]
            }
        },
        "knn": {
            "field": "ml.inference.body_content.predicted_value",
            "k": 1,
            "num_candidates": 20,
            "query_vector_builder": {
                "text_embedding": {
                    "model_id": "sentence-transformers__all-distilroberta-v1",
                    "model_text": query_text
                }
            },
            "boost": 24
        },
        "_source": False, # Ensures that the source content is not included in the response
        "fields": ["title", "body_content", "url"], # Specifies the fields to be returned
        "size": 1 # Limits the number of search results returned
    }

    index = 'search-elastic-docs'
    resp = es.search(index=index, body=body)

    # Check if any hits were returned
    if resp['hits']['hits']:
        body_content = resp['hits']['hits'][0]['fields']['body_content'][0]
        url = resp['hits']['hits'][0]['fields']['url'][0]
    else:
        # Handle case where no results are found
        # body_content = "No relevant documents found."
        # url = "No URL available."
        body_content = resp
        url = "No URL available."

    return body_content, url

if __name__ == "__main__":
    query_text = "What is the experience of the candidate?"
    body_content, url = search(query_text)
    print(body_content)
    print(url)