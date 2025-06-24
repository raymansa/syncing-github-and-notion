from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Customer:
    id: str
    company_name: str
    crm_phase: str
    initial_project_idea: str
    next_step_summary: Optional[str] = ""

@dataclass
class Stakeholder:
    id: str
    stakeholder_name: str
    stakeholder_phase: str
    purpose: str
    next_step_summary: Optional[str] = ""

@dataclass
class Project:
    id: str
    project_name: str
    description:str
    status: str
    stage: str

@dataclass
class Task:
    id: str
    title: str
    status: str
    entity_name: Optional[str] = ""
    responsible_name: Optional[str] = ""
    planned_end_date: Optional[str] = None

@dataclass
class DashboardData:
    customers: List[Customer] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

# ... (keep existing dataclasses: Customer, Project, etc.)

@dataclass
class User:
    """Represents an authentication user stored in Firestore."""
    id: Optional[str]  # The Firestore document ID
    email: str
    password_hash: str