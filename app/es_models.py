from elasticsearch import Elasticsearch
from datetime import datetime
import os

def get_es_client():
    es_host = os.environ.get('ES_HOST', 'localhost')
    es_port = os.environ.get('ES_PORT', '9200')
    
    return Elasticsearch([f"http://{es_host}:{es_port}"])

def create_es_indices():
    es = get_es_client()
    
    employee_mapping = {
        "mappings": {
            "properties": {
                "employee_id": {"type": "keyword"},
                "individual_id": {"type": "keyword"}
            }
        }
    }
    
    location_mapping = {
        "mappings": {
            "properties": {
                "individual_id": {"type": "keyword"},
                "timestamp": {"type": "date"},
                "location": {"type": "geo_point"},
                "longitude": {"type": "float"},
                "latitude": {"type": "float"}
            }
        }
    }
    
    if es.indices.exists(index="employee_individual_map"):
        es.indices.delete(index="employee_individual_map")
    es.indices.create(index="employee_individual_map", body=employee_mapping)
    
    if es.indices.exists(index="locations"):
        es.indices.delete(index="locations")
    es.indices.create(index="locations", body=location_mapping)
    
    return es