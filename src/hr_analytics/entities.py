from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date
from typing import Any, Dict, Optional


@dataclass
class Employee:
    employee_id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    department: str = ""
    role: str = ""
    salary: float = 0.0
    hire_date: Optional[date] = None
    manager_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Project:
    project_id: Optional[int] = None
    project_name: str = ""
    department: str = ""
    priority: str = "Medium"
    budget: float = 0.0
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Review:
    review_id: Optional[int] = None
    employee_id: int = 0
    review_date: Optional[date] = None
    performance_score: float = 0.0
    manager_comment: str = ""
    department: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
