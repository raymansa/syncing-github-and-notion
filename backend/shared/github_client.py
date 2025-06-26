from github import Github, Auth
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

class GitHubClient:
    def __init__(self, token: str):
        self.rest_client = Github(auth=Auth.Token(token))
        self.user = self.rest_client.get_user()
        
        self._transport = RequestsHTTPTransport(
            url="https://api.github.com/graphql",
            headers={"Authorization": f"Bearer {token}"},
            use_json=True,
        )
        self.graphql_client = Client(transport=self._transport, fetch_schema_from_transport=True)

    def get_all_repos(self) -> list[str]:
        print("Retrieving repositories from GitHub...")
        return [repo.name for repo in self.user.get_repos()]

    def get_all_projects(self) -> list[dict]:
        print("Retrieving projects from GitHub...")
        query = gql("""
            query GetUserProjects($login: String!) {
                user(login: $login) {
                    projectsV2(first: 100) { nodes { id title } }
                }
            }
        """)
        result = self.graphql_client.execute(query, variable_values={"login": self.user.login})
        return result['user']['projectsV2']['nodes']

    def create_repo(self, name: str, description: str):
        print(f"Creating GitHub repository: {name}...")
        return self.user.create_repo(name=name, description=description, private=False)

    def create_project(self, title: str) -> str:
        print(f"Creating GitHub project: {title}...")
        mutation = gql("""
            mutation CreateProject($ownerId: ID!, $title: String!) {
                createProjectV2(input: {ownerId: $ownerId, title: $title}) {
                    projectV2 { id }
                }
            }
        """)
        result = self.graphql_client.execute(mutation, variable_values={"ownerId": self.user.node_id, "title": title})
        return result['createProjectV2']['projectV2']['id']
    
    def create_issue(self, repo_name: str, title: str, body: str):
        repo = self.user.get_repo(repo_name)
        return repo.create_issue(title=title, body=body)

    def add_issue_to_project(self, project_id: str, issue_node_id: str):
        print(f"Adding issue to project {project_id}...")
        mutation = gql("""
            mutation AddItemToProject($projectId: ID!, $contentId: ID!) {
                addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
                    item { id }
                }
            }
        """)
        self.graphql_client.execute(mutation, variable_values={"projectId": project_id, "contentId": issue_node_id})

    # ... (Add update logic here later) ...