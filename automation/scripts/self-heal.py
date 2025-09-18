import os
import time
from datetime import datetime
from elasticsearch import Elasticsearch

# --- Environment Setup ---
# In a real-world scenario, these would be configured securely
ELASTIC_HOST = os.environ.get("ELASTIC_HOST", "localhost")
ELASTIC_PORT = int(os.environ.get("ELASTIC_PORT", 9200))

# --- Elasticsearch Connection ---
es = Elasticsearch([{'host': ELASTIC_HOST, 'port': ELASTIC_PORT}])

def check_service_health(service_name):
    """
    Checks the health of a service.
    This is a mock function. In a real-world scenario, this would
    involve making an API call to a health check endpoint.
    """
    print(f"Checking health of {service_name}...")
    # Simulate a service that is sometimes unhealthy
    if datetime.now().minute % 5 == 0:
        return "unhealthy"
    return "healthy"

def restart_service(service_name):
    """
    Restarts a service.
    This is a mock function. In a real-world scenario, this would
    involve making an API call to a container orchestrator like Kubernetes.
    """
    print(f"Restarting {service_name}...")
    time.sleep(2)
    print(f"{service_name} restarted.")
    return True

def log_to_elk(index, message):
    """
    Logs a message to Elasticsearch.
    """
    try:
        es.index(index=index, body=message)
        print(f"Logged to ELK: {message}")
    except Exception as e:
        print(f"Error logging to ELK: {e}")

def perform_root_cause_analysis(service_name):
    """
    Performs a basic root cause analysis by querying logs from ELK.
    """
    print(f"Performing RCA for {service_name}...")
    # In a real-world scenario, you would have more sophisticated queries
    # and analysis, potentially involving machine learning models.
    try:
        # Look for recent error logs
        res = es.search(
            index="logs-*",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"service.name": service_name}},
                            {"match": {"log.level": "error"}},
                        ],
                        "filter": {
                            "range": {
                                "@timestamp": {
                                    "gte": "now-5m"
                                }
                            }
                        }
                    }
                },
                "size": 10,
                "sort": [{"@timestamp": {"order": "desc"}}]
            }
        )
        if res['hits']['hits']:
            print("--- Potential Root Causes (from ELK logs) ---")
            for hit in res['hits']['hits']:
                print(f"- {hit['_source']['@timestamp']}: {hit['_source']['message']}")
            return res['hits']['hits'][0]['_source']['message']
        else:
            print("No recent error logs found in ELK for this service.")
            return "No specific error logs found."
    except Exception as e:
        print(f"Error performing RCA with ELK: {e}")
        return "Could not connect to ELK for RCA."


def main():
    """
    Main function for the self-healing script.
    """
    service_name = "web-app"
    while True:
        health = check_service_health(service_name)
        if health == "unhealthy":
            print(f"{service_name} is unhealthy. Taking corrective action.")
            
            # 1. Perform RCA
            rca_summary = perform_root_cause_analysis(service_name)
            
            # 2. Log the incident
            incident_log = {
                "@timestamp": datetime.utcnow().isoformat(),
                "service.name": service_name,
                "event.kind": "alert",
                "event.action": "self_healing_triggered",
                "message": f"Service {service_name} detected as unhealthy.",
                "rca.summary": rca_summary
            }
            log_to_elk("incidents", incident_log)

            # 3. Attempt to restart the service
            restarted = restart_service(service_name)

            # 4. Log the outcome
            outcome_log = {
                "@timestamp": datetime.utcnow().isoformat(),
                "service.name": service_name,
                "event.kind": "action_result",
                "event.action": "restart_service",
                "event.outcome": "success" if restarted else "failure",
                "message": f"Attempted to restart {service_name}. Success: {restarted}"
            }
            log_to_elk("incidents", outcome_log)

        else:
            print(f"{service_name} is healthy.")
        
        time.sleep(60)

if __name__ == "__main__":
    main()

