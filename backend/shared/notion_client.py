import requests
from .data_models import DashboardData, Customer, Project, Task

class NotionClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def _query_database(self, db_id: str) -> dict:
        """Helper to query a database."""
        url = f"{self.base_url}/databases/{db_id}/query"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()

    def get_all_dashboard_data(self) -> DashboardData:
        """Fetches all data needed for the dashboard and transforms it."""
        # In a real implementation, you'd query multiple DBs
        # customer_data = self._query_database("YOUR_CUSTOMER_DB_ID")
        # project_data = self._query_database("YOUR_PROJECT_DB_ID")
        # task_data = self._query_database("YOUR_TASK_DB_ID")

        # For this example, we'll use mock data.
        # Replace this with your actual data transformation logic.
        mock_customers = [Customer(id="1", company_name="Excellerate", crm_phase="Concept", initial_project_idea="AI-driven insights")]
        mock_projects = [Project(id="1", project_name="Synapse", status="Active", stage="Planning", description="AI-driven project management tool")]
        mock_tasks = [Task(id="1", title="Define Business Model", status="Not started", entity_name="Nueroflux")]

        return DashboardData(
            customers=mock_customers,
            projects=mock_projects,
            tasks=mock_tasks
        )