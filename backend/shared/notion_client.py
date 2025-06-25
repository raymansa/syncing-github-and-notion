import requests
from .data_models import DashboardData, Customer, Project, Task, Stakeholder, SyncLog, WeeklyReport

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
        mock_customers = [
            Customer(
                id="1",
                company_name="Excellerate",
                crm_phase="Concept/Demo Presentation",
                initial_project_idea="AI-driven insights",
                status="In Progress",
                next_step_summary="Send final proposal document"
            ),
            Customer(
                id="2",
                company_name="Customer C",
                crm_phase="Initiation",
                initial_project_idea="Nueroflux will provide Excellerate Services with the performance management code",
                status="In Progress",
                next_step_summary="Get in touch with Service Provider"
            ),
            Customer(
                id="3",
                company_name="Customer D",
                crm_phase="Concept/Demo Presentation",
                initial_project_idea="Nueroflux will provide Excellerate Services with the performance management code",
                status="In Progress",
                next_step_summary="Send final proposal document"
            ),
        ]

        mock_projects = [
            Project(
                id="1",
                project_name="Syncing Github and Notion",
                description="Process Step: 01. Client Needs Analysis",
                status="Potential",
                stage="Planning & Design",
                manager="Rendani",
                customer="",
                process_step="01. Client Needs Analysis",
                characteristics=[
                    {
                        "quality": "When a new project is created in notion, a new repository and project is created in github.",
                        "features": ["Create GitHub repository and project"]
                    },
                    {
                        "quality": "When a new feature is added or updated in the notion project db, automatically make the update to GitHub",
                        "features": ["Update GitHub Project Table"]
                    },
                    {
                        "quality": "The project works as a standalone application, first locally and then eventually online",
                        "features": [
                            "The application automatically runs on a periodic basis",
                            "Secret keys are stored securely in order to allow the application to run automatically"
                        ]
                    }
                  ]
            ),
            Project(
                id="2",
                project_name="RepatriaTrack",
                description="Process Step: 01. Client Needs Analysis",
                status="Potential",
                stage="Execution (Active)",
                manager="Rendani",
                customer="South African Government",
                process_step="01. Client Needs Analysis",
                characteristics=[
                    {
                        "quality": "When a new project is created in notion, a new repository and project is created in github.",
                        "features": ["Create GitHub repository and project"]
                    },
                    {
                        "quality": "When a new feature is added or updated in the notion project db, automatically make the update to GitHub",
                        "features": ["Update GitHub Project Table"]
                    },
                    {
                        "quality": "The project works as a standalone application, first locally and then eventually online",
                        "features": [
                            "The application automatically runs on a periodic basis",
                            "Secret keys are stored securely in order to allow the application to run automatically"
                        ]
                    }
                ]
            ),
            Project(
                id="3",
                project_name="Mining Performance App",
                description="Process Step: 01. Client Needs Analysis",
                status="Potential",
                stage="On Hold / Blocked",
                manager="Rendani",
                customer="Department of Agriculture, Land Reform and Rural Development",
                process_step="01. Client Needs Analysis",
                characteristics=[
                    {
                        "quality": "When a new project is created in notion, a new repository and project is created in github.",
                        "features": ["Create GitHub repository and project"]
                    },
                    {
                        "quality": "When a new feature is added or updated in the notion project db, automatically make the update to GitHub",
                        "features": ["Update GitHub Project Table"]
                    },
                    {
                        "quality": "The project works as a standalone application, first locally and then eventually online",
                        "features": [
                            "The application automatically runs on a periodic basis",
                            "Secret keys are stored securely in order to allow the application to run automatically"
                        ]
                    }
                ]
            ),
        ]
        
        mock_tasks = [
            Task(
                id="1",
                title="Create GitHub repository and project",
                type="Task",
                status="In Progress",
                entity_name="Syncing G&N",
                responsible_name="Rendani",
                important="Urgent",
                priority="High",
                planned_end_date="2023-11-10"
            ),
            Task(
                id="2",
                title="Update GitHub Project Table",
                type="Task",
                status="To Do",
                entity_name="Syncing G&N",
                responsible_name="Rendani",
                important="Important and Urgent",
                priority="Medium",
                planned_end_date="2023-11-15"
            ),
            Task(
                id="3",
                title="Draft DALRRD proposal",
                type="Task",
                status="Done",
                entity_name="RepatriaTrack",
                responsible_name="Alex",
                important="Important",
                priority="Low",
                planned_end_date="2023-11-05"
            ),
        ]
        
        mock_stakeholders=[
            Stakeholder(id = 1, stakeholder_name = "Stakeholder A", stakeholder_phase = "1. Initiation Meeting", purpose = "Define project scope and objectives",  next_step_summary= "Get the registered on the books", status="In Progress"), 
            Stakeholder(id = 2, stakeholder_name = "Stakeholder C", stakeholder_phase = "2. Defining the Relationship", purpose = "Gaining information on the services industry from the stakeholders perspective",  next_step_summary= "Schedule product demo", status="In Progress"),]
        
        mock_sync_logs = [
            SyncLog(id="1", timestamp="2025-06-25 09:00:00", message="Created GitHub repository for project Synapse", status="success"),
            SyncLog(id="2", timestamp="2025-06-25 09:05:00", message="Updated Notion task: Define Business Model", status="success"),
            SyncLog(id="3", timestamp="2025-06-25 09:10:00", message="Synced status: Success", status="success"),
            SyncLog(id="4", timestamp="2025-06-25 09:15:00", message="Error: Could not update GitHub Project", status="error"),
        ]

        return DashboardData(
            customers=mock_customers,
            projects=mock_projects,
            tasks=mock_tasks,
            stakeholders = mock_stakeholders,
            sync_logs=mock_sync_logs,
        )