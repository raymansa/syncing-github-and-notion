import os
import sys
from github import Github
from .github_oauth_handler import get_github_token

# Add parent directory to path to import shared modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.secrets import get_secret
from shared.notion_client import NotionClient
from shared.github_client import GitHubClient
from shared.data_models import Feature

def _create_and_add_feature_to_project(github_client: GitHubClient, repo_name: str, project_id: str, feature: Feature):
    """Helper function to create a GitHub issue and add it to a project."""
    print(f"  - Creating issue for feature: '{feature.name}'")
    issue = github_client.create_issue(repo_name, feature.name, feature.content)
    github_client.add_issue_to_project(project_id, issue.node_id)
    print(f"  - Successfully added '{feature.name}' to project.")

def run():
    """Main function for the GitHub Sync Worker."""
    print("--- GitHub Sync Worker Started ---")
    
    # --- 1. Initialization ---
    gcp_project_id = os.getenv("GCP_PROJECT_ID")
    github_token = get_github_token() # Handles OAuth flow
    
    if not github_token:
        print("Could not obtain GitHub token. Exiting.")
        return
    
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
            print(f"\n[CREATE] Project '{project_name}' not found in GitHub. Creating...")
            # 3.1 Create Repo and Project
            repo = github.create_repo(repo_name, f"Repo for {project_name}")
            project_id = github.create_project(project_name)
            print(f"Successfully created repo '{repo.full_name}' and project ID '{project_id}'")

            # 3.2 Create Issues from Features
            features = notion.get_features_for_project(project_page)
            for feature in features:
                _create_and_add_feature_to_project(github, repo_name, project_id, feature)
        else:
            # UPDATE FLOW
            print(f"\n[UPDATE] Project '{project_name}' exists. Checking for updates...")
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
    
    print("\n--- GitHub Sync Worker Finished ---")

if __name__ == "__main__":
    run()