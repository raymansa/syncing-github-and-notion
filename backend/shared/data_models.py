from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Customer:
    id: str
    company_name: str
    crm_phase: str
    initial_project_idea: str
    next_step_summary: Optional[str] = ""
    status: Optional[str] = ""

@dataclass
class Stakeholder:
    id: str
    stakeholder_name: str
    stakeholder_phase: str
    purpose: str
    next_step_summary: Optional[str] = ""
    status: Optional[str] = ""

@dataclass
class Project:
    id: str
    project_name: str
    description:str
    status: str
    stage: str
    manager: str
    customer: str
    process_step: str
    characteristics: List[dict]

@dataclass
class Task:
    id: str
    title: str
    type: str
    status: str
    entity_name: Optional[str] = ""
    responsible_name: Optional[str] = ""
    important: Optional[str] = ""
    priority: Optional[str] = ""
    planned_end_date: Optional[str] = None

@dataclass
class SyncLog:
    id: str
    timestamp: str
    message: str
    status: str

@dataclass
class User:
    """Represents an authentication user stored in Firestore."""
    id: Optional[str]  # The Firestore document ID
    email: str
    password_hash: str

@dataclass
class WeeklyReport:
    generated_on: str
    projects: list
    customers: list
    stakeholders: list
    tasks: list

@dataclass
class DashboardData:
    customers: List[Customer] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    stakeholders: List[Stakeholder] = field(default_factory=list)
    sync_logs: List[SyncLog] = field(default_factory=list)
    weekly_report: WeeklyReport = None

@dataclass
class Feature:
    id: str
    name: str
    status: str
    content: str 

@dataclass
class QualityCharacteristic:
    """Represents a high-level requirement or user need."""
    id: str
    name: str
    user_story: str
    feature_ids: List[str] = field(default_factory=list)
    feature_names: List[str] = field(default_factory=list)  # <-- Add this line