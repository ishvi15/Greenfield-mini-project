DEPARTMENTS = (
    "Engineering",
    "People",
    "Finance",
    "Sales",
    "Operations",
    "Marketing",
)

DEPARTMENT_ALIASES = {
    "r&dd": "Research & Development",
    "r&d": "Research & Development",
    "research and development": "Research & Development",
    "research & development": "Research & Development",
    "human resources": "Human Resources",
}


def normalize_department(value: object) -> str:
    department = " ".join(str(value).split()).strip()
    return DEPARTMENT_ALIASES.get(department.casefold(), department)