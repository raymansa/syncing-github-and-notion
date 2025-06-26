import os
import sys
import json
import logging
from datetime import datetime
from github import Github
from .github_oauth_handler import get_github_token

# Add parent directory to path to import shared modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.secrets import get_secret
from shared.notion_client import NotionClient
from shared.github_client import GitHubClient
from shared.data_models import Feature

# --- Structured Logging Setup ---
def log_action(service: str, action: str, status: str, details: str):
    """Creates a structured log entry as a JSON string."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": service,
        "action": action,
        "status": status,
        "details": details,
        # This payload structure is what the GCP Logging client will look for
        "jsonPayload": {
            "service": service,
            "action": action,
            "status": status,
            "details": details
        }
    }
    # Print the JSON string to stdout, which Cloud Logging will pick up
    print(json.dumps(log_entry))

def _create_and_add_feature_to_project(github_client: GitHubClient, repo_name: str, project_id: str, feature: Feature):
    """Helper function to create a GitHub issue and add it to a project."""
    log_action("GitHub Sync Worker", "CREATE_ISSUE", "INFO", f"Creating issue for feature: '{feature.name}'")
    issue = github_client.create_issue(repo_name, feature.name, feature.content)
    github_client.add_issue_to_project(project_id, issue.node_id)
    log_action("GitHub Sync Worker", "ADD_TO_PROJECT", "SUCCESS", f"Successfully added '{feature.name}' to project.")

def run():
    """Main function for the GitHub Sync Worker."""
    service_name = "GitHub Sync Worker"
    log_action(service_name, "WORKER_START", "INFO", "GitHub Sync Worker process started.")
    
    try: 
        # --- 1. Initialization ---
        gcp_project_id = os.getenv("GCP_PROJECT_ID")
        github_token = get_github_token() # Handles OAuth flow
        
        if not github_token:
            raise Exception("Could not obtain GitHub token.")

        
        # Fetch the new secret
        projects_db_id = get_secret("PROJECTS_DB_ID", project_id=gcp_project_id)

        notion = NotionClient(
            api_key=get_secret("NOTION_API_KEY", project_id=gcp_project_id),
            projects_db_id=projects_db_id
        )
        github = GitHubClient(token=github_token)

        # --- 2. Fetch Initial State ---
        notion_projects = notion.get_active_projects()
        github_repos = github.get_all_repos()
        github_projects_map = {p['title']: p for p in github.get_all_projects()}

        # --- 3. Sync Loop ---
        for project_page in notion_projects:
            project_name = project_page['properties']['Project Name']['title'][0]['plain_text']
            repo_name = project_name.replace(" ", "-").lower()

            if repo_name not in github_repos:
                # CREATE FLOW
                log_action(service_name, "CREATE_REPO", "INFO", f"Project '{project_name}' not found. Creating...")
                # 3.1 Create Repo and Project
                repo = github.create_repo(repo_name, f"Repo for {project_name}")
                project_id = github.create_project(project_name)
                log_action(service_name, "CREATE_PROJECT", "SUCCESS", f"Created repo '{repo.full_name}' and project ID '{project_id}'")

                # 3.2 Create Issues from Features
                features = notion.get_features_for_project(project_page)
                for feature in features:
                    _create_and_add_feature_to_project(github, repo_name, project_id, feature)
            else:
                # UPDATE FLOW
                log_action(service_name, "UPDATE_PROJECT", "INFO", f"Project '{project_name}' exists. Checking for updates.")
                if project_name in github_projects_map:
                    print(f"Warning: Repo '{repo_name}' exists but project '{project_name}' does not. Skipping update.")
                    continue

                # This is where the logic from update_github_projects.js is implemented.
                project_id = github_projects_map[project_name]['id']
                github_items = github.get_project_items(project_id)
                github_items_map = {item['content']['title']: item['content'] for item in github_items}
                
                notion_features = notion.get_features_for_project(project_page)

                for feature in notion_features:
                    existing_item = github_items_map.get(feature.name)

                    if existing_item:
                        # Item exists, check if content needs updating
                        if existing_item['body'] != feature.content:
                            print(f"  - Updating content for item: '{feature.name}'")
                            github.update_issue_body(existing_item['id'], feature.content)
                        else:
                            print(f"  - Item '{feature.name}' is already up-to-date.")
                    else:
                        # Item does not exist, create it
                        print(f"  - New feature '{feature.name}' found for existing project.")
                        _create_and_add_feature_to_project(github, repo_name, project_id, feature)
    except Exception as e:
        log_action(service_name, "WORKER_FAILURE", "FAILED", f"An unexpected error occurred: {str(e)}")
    
    log_action(service_name, "WORKER_END", "INFO", "GitHub Sync Worker process finished.")
    
    print("\n--- GitHub Sync Worker Finished ---")

if __name__ == "__main__":
    run()