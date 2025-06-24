import os
from flask import Flask, jsonify, request, abort
from cachetools import TTLCache
from dataclasses import asdict

from shared.secrets import get_secret
from shared.notion_client import NotionClient

# --- Initialization ---
app = Flask(__name__)

# In-memory cache with a 10-minute time-to-live and max size of 10 items
cache = TTLCache(maxsize=10, ttl=600)

# Load secrets
# Note: For production on GCP, set the PROJECT_ID environment variable
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
NOTION_API_KEY = get_secret("NOTION_API_KEY", project_id=GCP_PROJECT_ID)
INTERNAL_API_KEY = get_secret("INTERNAL_API_KEY", project_id=GCP_PROJECT_ID) # Used for API auth

# Instantiate clients
notion = NotionClient(api_key=NOTION_API_KEY)

# --- Authentication ---
@app.before_request
def require_api_key():
    # Allow public access for a simple health check endpoint
    if request.endpoint == 'health_check':
        return
        
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != INTERNAL_API_KEY:
        abort(401, description="Invalid or missing API Key.")

# --- API Endpoints ---
@app.route("/")
def health_check():
    return "Project Synapse API is healthy!"

@app.route("/v1/dashboard", methods=["GET"])
def get_dashboard_data():
    """
    Endpoint to get all data for the main dashboard.
    It uses an in-memory cache to avoid excessive calls to the Notion API.
    """
    cache_key = "dashboard_data"
    
    # Check cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        print("Returning data from cache.")
        return jsonify(asdict(cached_data))

    # If cache miss, fetch from Notion
    print("Cache miss. Fetching data from Notion.")
    dashboard_data = notion.get_all_dashboard_data()
    
    # Store result in cache
    cache[cache_key] = dashboard_data

    return jsonify(asdict(dashboard_data))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))