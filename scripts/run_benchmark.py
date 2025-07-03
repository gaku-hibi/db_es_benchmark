import sys
import os
sys.path.append('/app')

from models import get_session, Location, EmployeeIndividualMap
from es_models import get_es_client
from datetime import datetime, timedelta
import time
import random
from sqlalchemy import and_, or_
import statistics

class BenchmarkRunner:
    def __init__(self):
        self.session = get_session()
        self.es = get_es_client()
        
    def measure_time(self, func):
        start = time.time()
        result = func()
        end = time.time()
        return end - start, result
    
    def benchmark_pg_individual_location_by_time(self, individual_id, start_time, end_time):
        def query():
            return self.session.query(Location).filter(
                and_(
                    Location.individual_id == individual_id,
                    Location.timestamp >= start_time,
                    Location.timestamp <= end_time
                )
            ).all()
        return self.measure_time(query)
    
    def benchmark_es_individual_location_by_time(self, individual_id, start_time, end_time):
        def query():
            body = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"individual_id": individual_id}},
                            {"range": {
                                "timestamp": {
                                    "gte": start_time.isoformat(),
                                    "lte": end_time.isoformat()
                                }
                            }}
                        ]
                    }
                },
                "size": 10000
            }
            return self.es.search(index="locations", body=body)
        return self.measure_time(query)
    
    def benchmark_pg_location_by_area(self, min_lat, max_lat, min_lon, max_lon):
        def query():
            return self.session.query(Location).filter(
                and_(
                    Location.latitude >= min_lat,
                    Location.latitude <= max_lat,
                    Location.longitude >= min_lon,
                    Location.longitude <= max_lon
                )
            ).all()
        return self.measure_time(query)
    
    def benchmark_es_location_by_area(self, min_lat, max_lat, min_lon, max_lon):
        def query():
            body = {
                "query": {
                    "geo_bounding_box": {
                        "location": {
                            "top_left": {
                                "lat": max_lat,
                                "lon": min_lon
                            },
                            "bottom_right": {
                                "lat": min_lat,
                                "lon": max_lon
                            }
                        }
                    }
                },
                "size": 10000
            }
            return self.es.search(index="locations", body=body)
        return self.measure_time(query)
    
    def benchmark_pg_complex_query(self, individual_ids, start_time, end_time):
        def query():
            return self.session.query(Location).filter(
                and_(
                    Location.individual_id.in_(individual_ids),
                    Location.timestamp >= start_time,
                    Location.timestamp <= end_time
                )
            ).all()
        return self.measure_time(query)
    
    def benchmark_es_complex_query(self, individual_ids, start_time, end_time):
        def query():
            body = {
                "query": {
                    "bool": {
                        "must": [
                            {"terms": {"individual_id": individual_ids}},
                            {"range": {
                                "timestamp": {
                                    "gte": start_time.isoformat(),
                                    "lte": end_time.isoformat()
                                }
                            }}
                        ]
                    }
                },
                "size": 10000
            }
            return self.es.search(index="locations", body=body)
        return self.measure_time(query)
    
    def run_benchmark_suite(self, num_iterations=10):
        results = {
            'individual_time_range': {'pg': [], 'es': []},
            'location_area': {'pg': [], 'es': []},
            'complex_query': {'pg': [], 'es': []}
        }
        
        print(f"Running benchmark with {num_iterations} iterations for each query type...\n")
        
        for i in range(num_iterations):
            individual_id = f"IND{random.randint(1, 100):04d}"
            start_time = datetime(2023, random.randint(1, 12), random.randint(1, 28))
            end_time = start_time + timedelta(days=random.randint(1, 30))
            
            pg_time, pg_result = self.benchmark_pg_individual_location_by_time(individual_id, start_time, end_time)
            es_time, es_result = self.benchmark_es_individual_location_by_time(individual_id, start_time, end_time)
            
            results['individual_time_range']['pg'].append(pg_time)
            results['individual_time_range']['es'].append(es_time)
            
            if i == 0:
                print(f"Query 1 - Individual location by time range:")
                print(f"  PostgreSQL returned {len(pg_result)} records")
                print(f"  Elasticsearch returned {es_result['hits']['total']['value']} records")
        
        for i in range(num_iterations):
            base_lat = 35.6762
            base_lon = 139.6503
            delta = random.uniform(0.01, 0.05)
            
            min_lat = base_lat - delta
            max_lat = base_lat + delta
            min_lon = base_lon - delta
            max_lon = base_lon + delta
            
            pg_time, pg_result = self.benchmark_pg_location_by_area(min_lat, max_lat, min_lon, max_lon)
            es_time, es_result = self.benchmark_es_location_by_area(min_lat, max_lat, min_lon, max_lon)
            
            results['location_area']['pg'].append(pg_time)
            results['location_area']['es'].append(es_time)
            
            if i == 0:
                print(f"\nQuery 2 - Location by geographical area:")
                print(f"  PostgreSQL returned {len(pg_result)} records")
                print(f"  Elasticsearch returned {es_result['hits']['total']['value']} records")
        
        for i in range(num_iterations):
            num_individuals = random.randint(5, 20)
            individual_ids = [f"IND{random.randint(1, 100):04d}" for _ in range(num_individuals)]
            start_time = datetime(2023, random.randint(1, 12), random.randint(1, 28))
            end_time = start_time + timedelta(days=random.randint(7, 60))
            
            pg_time, pg_result = self.benchmark_pg_complex_query(individual_ids, start_time, end_time)
            es_time, es_result = self.benchmark_es_complex_query(individual_ids, start_time, end_time)
            
            results['complex_query']['pg'].append(pg_time)
            results['complex_query']['es'].append(es_time)
            
            if i == 0:
                print(f"\nQuery 3 - Complex query (multiple individuals + time range):")
                print(f"  PostgreSQL returned {len(pg_result)} records")
                print(f"  Elasticsearch returned {es_result['hits']['total']['value']} records")
        
        return results
    
    def print_results(self, results):
        print("\n" + "="*80)
        print("BENCHMARK RESULTS")
        print("="*80)
        
        for query_type, times in results.items():
            print(f"\n{query_type.replace('_', ' ').title()}:")
            
            pg_times = times['pg']
            es_times = times['es']
            
            pg_avg = statistics.mean(pg_times)
            es_avg = statistics.mean(es_times)
            
            pg_median = statistics.median(pg_times)
            es_median = statistics.median(es_times)
            
            pg_min = min(pg_times)
            es_min = min(es_times)
            
            pg_max = max(pg_times)
            es_max = max(es_times)
            
            print(f"\n  PostgreSQL:")
            print(f"    Average: {pg_avg*1000:.2f}ms")
            print(f"    Median:  {pg_median*1000:.2f}ms")
            print(f"    Min:     {pg_min*1000:.2f}ms")
            print(f"    Max:     {pg_max*1000:.2f}ms")
            
            print(f"\n  Elasticsearch:")
            print(f"    Average: {es_avg*1000:.2f}ms")
            print(f"    Median:  {es_median*1000:.2f}ms")
            print(f"    Min:     {es_min*1000:.2f}ms")
            print(f"    Max:     {es_max*1000:.2f}ms")
            
            print(f"\n  Performance Comparison:")
            if pg_avg < es_avg:
                ratio = es_avg / pg_avg
                print(f"    PostgreSQL is {ratio:.2f}x faster")
            else:
                ratio = pg_avg / es_avg
                print(f"    Elasticsearch is {ratio:.2f}x faster")

def wait_for_services():
    print("Waiting for services to be ready...")
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            session = get_session()
            session.execute("SELECT 1")
            session.close()
            
            es = get_es_client()
            es.info()
            
            print("Services are ready!")
            return True
        except Exception as e:
            retry_count += 1
            print(f"Waiting for services... ({retry_count}/{max_retries})")
            time.sleep(2)
    
    print("Services failed to start!")
    return False

def main():
    if not wait_for_services():
        sys.exit(1)
    
    print("\nChecking if data exists...")
    session = get_session()
    location_count = session.query(Location).count()
    session.close()
    
    if location_count == 0:
        print("No data found. Running seed script first...")
        import seed_data
        seed_data.main()
    else:
        print(f"Found {location_count} location records in database.")
    
    print("\nStarting benchmark...")
    runner = BenchmarkRunner()
    results = runner.run_benchmark_suite(num_iterations=10)
    runner.print_results(results)

if __name__ == "__main__":
    main()