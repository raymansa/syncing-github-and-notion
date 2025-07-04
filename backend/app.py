import os
from flask import Flask, jsonify, request, abort
from cachetools import TTLCache
from dataclasses import asdict
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from flask_cors import CORS
from google.cloud import logging_v2
from datetime import timedelta

from shared.secrets import get_secret
from shared.notion_client import NotionClient
from shared.firestore_client import FirestoreClient

# --- Initialization ---
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], supports_credentials=True)

# Load secrets
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
NOTION_API_KEY = get_secret("NOTION_API_KEY", project_id=GCP_PROJECT_ID)
INTERNAL_API_KEY = get_secret("INTERNAL_API_KEY", project_id=GCP_PROJECT_ID) # For inter-service auth if needed

# Setup the Flask-JWT-Extended extension
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_SECRET_KEY"] = get_secret("JWT_SECRET_KEY", project_id=GCP_PROJECT_ID)
jwt = JWTManager(app)

# In-memory cache with a 10-minute time-to-live
cache = TTLCache(maxsize=10, ttl=600)

# Instantiate clients
notion_db_id = get_secret("PROJECTS_DB_ID", project_id=GCP_PROJECT_ID)
notion = NotionClient(api_key=get_secret("NOTION_API_KEY", project_id=GCP_PROJECT_ID), projects_db_id=notion_db_id)
firestore = FirestoreClient()
logging_client = logging_v2.Client()

# --- Authentication Endpoints ---

@app.route("/v1/auth/register", methods=["POST"])
def register_user():
    """Endpoint to register a new user."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        abort(400, description="Email and password are required.")
    
    try:
        user = firestore.create_user(email=data['email'], password=data['password'])
        return jsonify({"message": f"User {user.email} created successfully."}), 201
    except ValueError as e:
        abort(409, description=str(e)) # 409 Conflict if user already exists

@app.route("/v1/auth/login", methods=["POST"])
def login_user():
    """Endpoint to authenticate a user and return a JWT."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        abort(400, description="Email and password are required.")

    user = firestore.get_user_by_email(email=data['email'])
    
    if user and firestore.verify_password(user.password_hash, data['password']):
        # Identity can be any data that is json serializable
        access_token = create_access_token(identity=user.email)
        return jsonify(token=access_token)
    
    return abort(401, description="Invalid credentials.")

@app.route("/v1/auth/logout", methods=["POST"])
@jwt_required()
def logout_user():
    """
    Client-side logout. In a stateless JWT setup, the server doesn't do much.
    For enhanced security, a token blocklist could be implemented here.
    """
    return jsonify({"message": "Logout successful. Please discard the token on the client side."})

# --- Protected API Endpoints ---

@app.route("/")
def health_check():
    return "Project Synapse API is healthy!"

@app.route("/v1/profile")
@jwt_required()
def get_profile():
    """A sample protected endpoint to test JWT authentication."""
    current_user_email = get_jwt_identity()
    return jsonify(logged_in_as=current_user_email), 200

@app.route("/v1/dashboard", methods=["GET"])
@jwt_required() # Protect the dashboard endpoint
def get_dashboard_data():
    print("JWT identity:", get_jwt_identity())
    """Endpoint to get all data for the main dashboard."""
    cache_key = "dashboard_data"
    cached_data = cache.get(cache_key)
    if cached_data:
        print("Returning data from cache.")
        return jsonify(asdict(cached_data))

    print("Cache miss. Fetching data from Notion.")
    dashboard_data = notion.get_all_dashboard_data()
    cache[cache_key] = dashboard_data

    return jsonify(asdict(dashboard_data))

@app.route("/v1/logs", methods=["GET"])
@jwt_required()
def get_logs():
    """Fetches structured logs from Google Cloud Logging."""
    limit = request.args.get('limit', 50, type=int)
    
    # Filter for logs created by our workers that have a jsonPayload
    # In production, you might filter by a specific log name
    log_filter = f'jsonPayload.service:"GitHub Sync Worker"'
    
    try:
        entries = logging_client.list_log_entries(
            resource_names=[f"projects/{GCP_PROJECT_ID}"],
            filter_=log_filter,
            order_by=logging_v2.DESCENDING,
            page_size=limit
        )
        
        logs_list = []
        for entry in entries:
            payload = entry.json_payload
            logs_list.append({
                "timestamp": payload.get("timestamp"),
                "service": payload.get("service"),
                "action": payload.get("action"),
                "status": payload.get("status"),
                "details": payload.get("details"),
            })

        return jsonify({
            "logs": logs_list,
            "pagination": {
                "total": len(logs_list), # Simplified pagination for now
                "limit": limit,
                "offset": 0
            }
        })
    except Exception as e:
        print(f"Error fetching logs from GCP: {e}")
        abort(500, description="Could not fetch logs.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))