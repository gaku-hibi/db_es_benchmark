import sys
import os
sys.path.append('/app')

from models import create_tables, get_session, EmployeeIndividualMap, Location
from es_models import create_es_indices, get_es_client
from datetime import datetime, timedelta
import random
import time
from tqdm import tqdm
from elasticsearch.helpers import bulk

def generate_location_data():
    print("Generating test data...")
    
    num_individuals = 100
    locations_per_individual = 10000
    
    base_lat = 35.6762  # Tokyo latitude
    base_lon = 139.6503  # Tokyo longitude
    
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 1, 1)
    
    data = []
    
    for i in range(num_individuals):
        individual_id = f"IND{i+1:04d}"
        employee_id = f"EMP{i+1:04d}"
        
        individual_data = {
            'employee_id': employee_id,
            'individual_id': individual_id,
            'locations': []
        }
        
        for j in range(locations_per_individual):
            timestamp = start_date + timedelta(
                seconds=random.randint(0, int((end_date - start_date).total_seconds()))
            )
            
            latitude = base_lat + random.uniform(-0.1, 0.1)
            longitude = base_lon + random.uniform(-0.1, 0.1)
            
            individual_data['locations'].append({
                'timestamp': timestamp,
                'latitude': latitude,
                'longitude': longitude
            })
        
        individual_data['locations'].sort(key=lambda x: x['timestamp'])
        data.append(individual_data)
    
    return data

def seed_postgresql(data):
    print("\nSeeding PostgreSQL database...")
    engine = create_tables()
    session = get_session()
    
    try:
        for individual_data in tqdm(data, desc="Inserting individuals"):
            emp_individual = EmployeeIndividualMap(
                employee_id=individual_data['employee_id'],
                individual_id=individual_data['individual_id']
            )
            session.add(emp_individual)
        
        session.commit()
        
        for individual_data in tqdm(data, desc="Inserting locations"):
            locations = []
            for loc in individual_data['locations']:
                location = Location(
                    individual_id=individual_data['individual_id'],
                    timestamp=loc['timestamp'],
                    latitude=loc['latitude'],
                    longitude=loc['longitude']
                )
                locations.append(location)
            
            session.bulk_save_objects(locations)
            session.commit()
        
        print(f"PostgreSQL seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding PostgreSQL: {e}")
        session.rollback()
    finally:
        session.close()

def seed_elasticsearch(data):
    print("\nSeeding Elasticsearch...")
    es = create_es_indices()
    
    try:
        employee_actions = []
        for individual_data in data:
            action = {
                "_index": "employee_individual_map",
                "_source": {
                    "employee_id": individual_data['employee_id'],
                    "individual_id": individual_data['individual_id']
                }
            }
            employee_actions.append(action)
        
        bulk(es, employee_actions)
        print(f"Inserted {len(employee_actions)} employee-individual mappings")
        
        for individual_data in tqdm(data, desc="Inserting locations to ES"):
            location_actions = []
            for loc in individual_data['locations']:
                action = {
                    "_index": "locations",
                    "_source": {
                        "individual_id": individual_data['individual_id'],
                        "timestamp": loc['timestamp'].isoformat(),
                        "latitude": loc['latitude'],
                        "longitude": loc['longitude'],
                        "location": {
                            "lat": loc['latitude'],
                            "lon": loc['longitude']
                        }
                    }
                }
                location_actions.append(action)
            
            bulk(es, location_actions)
        
        es.indices.refresh(index="employee_individual_map")
        es.indices.refresh(index="locations")
        
        print(f"Elasticsearch seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding Elasticsearch: {e}")

def main():
    print("Starting data seeding process...")
    print(f"Generating data for {100} individuals with {10000} locations each...")
    
    start_time = time.time()
    
    data = generate_location_data()
    
    print(f"\nData generation took {time.time() - start_time:.2f} seconds")
    
    pg_start = time.time()
    seed_postgresql(data)
    print(f"PostgreSQL seeding took {time.time() - pg_start:.2f} seconds")
    
    es_start = time.time()
    seed_elasticsearch(data)
    print(f"Elasticsearch seeding took {time.time() - es_start:.2f} seconds")
    
    print(f"\nTotal seeding time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()