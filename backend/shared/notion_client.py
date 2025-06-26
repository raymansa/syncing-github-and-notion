import requests
from .data_models import DashboardData, Customer, Project, Task, Stakeholder, SyncLog, Feature, QualityCharacteristic
from shared.secrets import get_secret

class NotionClient:
    def __init__(self, api_key: str, projects_db_id: str):
        self.api_key = api_key
        self.projects_db_id = projects_db_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def _query_database(self, db_id: str, filter_payload: dict = None) -> dict:
        """Helper to query a database."""
        url = f"{self.base_url}/databases/{db_id}/query"
        request_body = {"filter": filter_payload} if filter_payload else {}
        response = requests.post(url, headers=self.headers, json=request_body if filter_payload else {})
        response.raise_for_status()
        return response.json()
    
    def _get_page(self, page_id: str):
        response = requests.get(f"{self.base_url}/pages/{page_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def _get_page_content_as_markdown(self, page_id: str) -> str:
        url = f"{self.base_url}/blocks/{page_id}/children"
        response = requests.get(url, headers=self.headers)
        blocks = response.json().get("results", [])
        markdown_lines = []
        for block in blocks:
            block_type = block.get("type")
            if block_type in block and block[block_type].get("rich_text"):
                text = "".join(t.get("plain_text", "") for t in block[block_type]["rich_text"])
                if block_type == "heading_1": markdown_lines.append(f"# {text}")
                elif block_type == "heading_2": markdown_lines.append(f"## {text}")
                elif block_type == "heading_3": markdown_lines.append(f"### {text}")
                elif block_type == "bulleted_list_item": markdown_lines.append(f"* {text}")
                elif block_type == "paragraph": markdown_lines.append(text)
        return "\n\n".join(markdown_lines)

    def get_active_projects(self) -> list:
        print("Retrieving active projects from Notion...")
        db_id = "YOUR_PROJECTS_DB_ID" # Replace with your actual DB ID from .env
        filter_payload = {"property": "Project Status", "select": {"equals": "Active"}}
        return self._query_database(self.projects_db_id, filter_payload).get("results", [])

    def get_features_for_project(self, project_page: dict) -> list[Feature]:
        print(f"Retrieving features for project: {project_page['properties']['Project Name']['title'][0]['plain_text']}...")
        features = []
        qc_relations = project_page['properties']['Quality Characteristic'].get('relation', [])
        
        for qc_ref in qc_relations:
            qc_page = self._get_page(qc_ref['id'])
            feature_relations = qc_page['properties']['Features'].get('relation', [])
            for feature_ref in feature_relations:
                feature_page = self._get_page(feature_ref['id'])
                if feature_page['properties']['Feature Status']['select']['name'] == 'Active':
                    title = feature_page['properties']['Feature']['title'][0]['plain_text']
                    content = self._get_page_content_as_markdown(feature_page['id'])
                    features.append(Feature(id=feature_page['id'], name=title, status='Active', content=content))
        print(f"Found {len(features)} active features.")
        return features
    
    def get_relation_names(self, relation_list, property_name="Next Steps"):
        """
        Given a Notion relation list, fetch and return the plain text(s) of the given property from the related page(s).
        """
        names = []
        for rel in relation_list:
            page = self._get_page(rel['id'])
            prop = page["properties"].get(property_name, {})
            # Try title, then rich_text
            if "title" in prop:
                names.append("".join([t.get("plain_text", "") for t in prop["title"]]))
            elif "rich_text" in prop:
                names.append("".join([t.get("plain_text", "") for t in prop["rich_text"]]))
        return ", ".join(names)
    
    def extract_notion_property_value(self, prop):
        """
        Given a Notion property dict, return a human-readable string value based on its type.
        """
        if not prop or not isinstance(prop, dict):
            return ""
        prop_type = prop.get("type")
        if not prop_type:
            return ""
        value = prop.get(prop_type)

        if prop_type == "title":
            return "".join([t.get("plain_text", "") for t in value]) if value else ""
        elif prop_type == "rich_text":
            return "".join([t.get("plain_text", "") for t in value]) if value else ""
        elif prop_type == "select":
            return value.get("name", "") if value else ""
        elif prop_type == "multi_select":
            return ", ".join([v.get("name", "") for v in value]) if value else ""
        elif prop_type == "status":
            return value.get("name", "") if value else ""
        elif prop_type == "date":
            return value.get("start", "") if value else ""
        elif prop_type == "people":
            return ", ".join([p.get("name", "") for p in value]) if value else ""
        elif prop_type == "files":
            return ", ".join([f.get("name", "") for f in value]) if value else ""
        elif prop_type == "checkbox":
            return "Yes" if value else "No"
        elif prop_type == "url":
            return value or ""
        elif prop_type == "number":
            return str(value) if value is not None else ""
        elif prop_type == "formula":
            # Formula can be of various types, handle common ones
            formula_type = value.get("type")
            return str(value.get(formula_type, "")) if formula_type else ""
        elif prop_type == "rollup":
            # Rollup can be array, number, date, etc.
            rollup_type = value.get("type")
            if rollup_type == "array":
                return ", ".join([self.extract_notion_property_value(i) for i in value.get("array", [])])
            elif rollup_type == "number":
                return str(value.get("number", ""))
            elif rollup_type == "date":
                return value.get("date", {}).get("start", "")
            else:
                return str(value.get(rollup_type, ""))
        elif prop_type == "relation":
            relation_list = value if value else []
            return self.get_relation_names(relation_list)
        elif prop_type == "unique_id":
            return str(value.get("number", "")) if value else ""
        else:
            return str(value) if value else ""
        
    def get_quality_characteristics_for_project(self, project_props):
        """
        Given a project's properties, fetch related Quality Characteristics and their features.
        Returns a list of QualityCharacteristic objects (with feature names).
        """
        characteristics = []
        qc_relations = project_props.get("Quality Characteristic", {}).get("relation", [])
        for qc_ref in qc_relations:
            qc_page = self._get_page(qc_ref['id'])
            qc_props = qc_page.get("properties", {})
            qc_name = ""
            if "Name" in qc_props and "title" in qc_props["Name"]:
                qc_name = "".join([t.get("plain_text", "") for t in qc_props["Name"]["title"]])
            user_story = ""
            if "User Story" in qc_props and "rich_text" in qc_props["User Story"]:
                user_story = "".join([t.get("plain_text", "") for t in qc_props["User Story"]["rich_text"]])
            features = []
            feature_ids = []
            feature_relations = qc_props.get("Features", {}).get("relation", [])
            for feature_ref in feature_relations:
                feature_page = self._get_page(feature_ref['id'])
                feature_props = feature_page.get("properties", {})
                feature_name = ""
                if "Feature" in feature_props and "title" in feature_props["Feature"]:
                    feature_name = "".join([t.get("plain_text", "") for t in feature_props["Feature"]["title"]])
                if feature_name:
                    features.append(feature_name)
                    feature_ids.append(feature_ref['id'])
            characteristics.append(QualityCharacteristic(
                id=qc_ref['id'],
                name=qc_name,
                user_story=user_story,
                feature_ids=feature_ids,
                feature_names=features,
            ))
        return characteristics

    def get_all_dashboard_data(self) -> DashboardData:
        """Fetches all data needed for the dashboard and transforms it."""

        # Fetch from Notion
        customer_data = self._query_database(get_secret("CRM_DB_ID"))
        project_data = self._query_database(get_secret("PROJECTS_DB_ID"))
        task_data = self._query_database(get_secret("TASKS_DB_ID"))
        stakeholder_data = self._query_database(get_secret("STAKEHOLDER_DB_ID"))

        # Customers
        customers = []
        for idx, row in enumerate(customer_data.get("results", [])):
            props = row["properties"]
            customers.append(Customer(
                id=row.get("id", str(idx)),
                company_name=self.extract_notion_property_value(props.get("Company Name")),
                crm_phase=self.extract_notion_property_value(props.get("CRM Phase")),
                initial_project_idea=self.extract_notion_property_value(props.get("Initial Project Idea")),
                status=self.extract_notion_property_value(props.get("Status")),
                next_step_summary=self.extract_notion_property_value(props.get("Meeting Next Steps")),
            ))

        # Projects
        projects = []
        for idx, row in enumerate(project_data.get("results", [])):
            props = row["properties"]
            projects.append(Project(
                id=row.get("id", str(idx)),
                project_name=self.extract_notion_property_value(props.get("Project Name")),
                description=self.extract_notion_property_value(props.get("Description")),
                status=self.extract_notion_property_value(props.get("Project Status")),
                stage=self.extract_notion_property_value(props.get("Stage")),
                manager=self.extract_notion_property_value(props.get("Project Manager")),
                customer=self.extract_notion_property_value(props.get("Customer")),
                process_step=self.extract_notion_property_value(props.get("Process Step")),
                characteristics=self.get_quality_characteristics_for_project(props),
            ))

        # Tasks
        tasks = []
        for idx, row in enumerate(task_data.get("results", [])):
            props = row["properties"]
            # for key, prop in props.items():
                # print(key, prop)
            tasks.append(Task(
                id=row.get("id", str(idx)),
                title=self.extract_notion_property_value(props.get("Title")),
                type=self.extract_notion_property_value(props.get("Task Type")),
                status=self.extract_notion_property_value(props.get("Status")),
                entity_name=self.extract_notion_property_value(props.get("Project")),
                responsible_name=self.extract_notion_property_value(props.get("Responsible")),
                important=self.extract_notion_property_value(props.get("Importance")),
                priority=self.extract_notion_property_value(props.get("Priority")),
                planned_end_date=self.extract_notion_property_value(props.get("Planned_End")),
            ))

        # Stakeholders
        stakeholders = []
        for idx, row in enumerate(stakeholder_data.get("results", [])):
            props = row["properties"]
            stakeholders.append(Stakeholder(
                id=row.get("id", str(idx)),
                stakeholder_name=self.extract_notion_property_value(props.get("Stakeholder Name")),
                stakeholder_phase=self.extract_notion_property_value(props.get("Stakeholder Phase")),
                purpose=self.extract_notion_property_value(props.get("Purpose")),
                next_step_summary=self.extract_notion_property_value(props.get("Next Steps")),
                status=self.extract_notion_property_value(props.get("Status")),
            ))
        
        mock_sync_logs = [
            SyncLog(id="1", timestamp="2025-06-25 09:00:00", message="Created GitHub repository for project Synapse", status="success"),
            SyncLog(id="2", timestamp="2025-06-25 09:05:00", message="Updated Notion task: Define Business Model", status="success"),
            SyncLog(id="3", timestamp="2025-06-25 09:10:00", message="Synced status: Success", status="success"),
            SyncLog(id="4", timestamp="2025-06-25 09:15:00", message="Error: Could not update GitHub Project", status="error"),
        ]

        return DashboardData(
            customers=customers,
            projects=projects,
            tasks=tasks,
            stakeholders=stakeholders,
            sync_logs=mock_sync_logs,
        )