from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from .db_manager import DatabaseConnection
from .entities import Employee, Project, Review


class BaseManager:
    def __init__(self):
        self.db = DatabaseConnection()


class EmployeeManager(BaseManager):
    def add_employee(self, employee: Employee) -> int:
        try:
            cursor = self.db.execute_query(
                """
                INSERT INTO employees (first_name, last_name, email, department, role_name, salary, hire_date, manager_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    employee.first_name,
                    employee.last_name,
                    employee.email,
                    employee.department,
                    employee.role,
                    employee.salary,
                    employee.hire_date,
                    employee.manager_id,
                ),
            )
            self.db.get_connection().commit()
            return cursor.lastrowid
        except Exception as exc:
            self.db.get_connection().rollback()
            raise RuntimeError(f"Failed to add employee: {exc}") from exc

    def get_employee(self, employee_id: int) -> Optional[Employee]:
        try:
            cursor = self.db.execute_query(
                "SELECT * FROM employees WHERE employee_id = %s",
                (employee_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return Employee(**row)
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch employee: {exc}") from exc

    def update_employee_department(self, employee_id: int, new_department: str) -> None:
        try:
            self.db.execute_query(
                "UPDATE employees SET department = %s WHERE employee_id = %s",
                (new_department, employee_id),
            )
            self.db.get_connection().commit()
        except Exception as exc:
            self.db.get_connection().rollback()
            raise RuntimeError(f"Failed to update department: {exc}") from exc


class ProjectManager(BaseManager):
    def add_project(self, project: Project) -> int:
        try:
            cursor = self.db.execute_query(
                """
                INSERT INTO projects (project_name, department, priority_level, budget, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    project.project_name,
                    project.department,
                    project.priority,
                    project.budget,
                    project.start_date,
                    project.end_date,
                ),
            )
            self.db.get_connection().commit()
            return cursor.lastrowid
        except Exception as exc:
            self.db.get_connection().rollback()
            raise RuntimeError(f"Failed to add project: {exc}") from exc


class AnalyticsManager(BaseManager):
    def get_performance_trend(self) -> List[Dict[str, Any]]:
        try:
            cursor = self.db.execute_query(
                """
                SELECT review_year, AVG(performance_score) AS avg_score
                FROM fact_performancereviews
                GROUP BY review_year
                ORDER BY review_year
                """
            )
            return cursor.fetchall()
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch performance trend: {exc}") from exc

    def get_top_employees(self) -> List[Dict[str, Any]]:
        try:
            cursor = self.db.execute_query(
                """
                SELECT employee_name, department, performance_score,
                       DENSE_RANK() OVER (PARTITION BY department ORDER BY performance_score DESC) AS dept_rank
                FROM fact_performancereviews
                ORDER BY department, dept_rank
                LIMIT 20
                """
            )
            return cursor.fetchall()
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch top employees: {exc}") from exc
