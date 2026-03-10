import requests
import json

BASE_URL = "http://localhost:8000/api"

def load_sample_data():
    # Load sample data
    with open('sample_data.json', 'r') as f:
        data = json.load(f)
    
    # Create project
    print("Creating project...")
    project_response = requests.post(
        f"{BASE_URL}/projects",
        json=data['project']
    )
    project = project_response.json()
    project_id = project['id']
    print(f"✓ Created project: {project['name']} (ID: {project_id})")
    
    # Add data sources
    print("\nAdding data sources...")
    for source in data['data_sources']:
        response = requests.post(
            f"{BASE_URL}/ingestion/{project_id}/manual",
            json=source
        )
        result = response.json()
        print(f"✓ Added {source['source_type']} data: {result['extracted_count']} items extracted")
    
    # Detect conflicts
    print("\nDetecting conflicts...")
    conflict_response = requests.post(
        f"{BASE_URL}/ingestion/{project_id}/detect-conflicts"
    )
    conflicts = conflict_response.json()
    print(f"✓ Detected {conflicts['count']} conflicts")
    
    # Generate BRD
    print("\nGenerating BRD...")
    doc_response = requests.post(
        f"{BASE_URL}/documents/{project_id}/generate"
    )
    document = doc_response.json()
    print(f"✓ Generated BRD version {document['version']}")
    
    # Get traceability matrix
    print("\nGenerating traceability matrix...")
    trace_response = requests.get(
        f"{BASE_URL}/documents/{project_id}/traceability"
    )
    matrix = trace_response.json()
    print(f"✓ Generated matrix with {len(matrix['matrix'])} requirements")
    
    print(f"\n✅ Sample data loaded successfully!")
    print(f"\nView the project at: http://localhost:3000/project/{project_id}")
    print(f"Document ID: {document['id']}")

if __name__ == "__main__":
    try:
        load_sample_data()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure the backend server is running:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")
