DEPARTMENTS = (
    "Research & Development",
    "Sales",
    "Human Resources",
)

DEPARTMENT_ALIASES = {
    "r&dd": "Research & Development",
    "r&d": "Research & Development",
    "research and development": "Research & Development",
    "research & development": "Research & Development",
    "human resources": "Human Resources",
    "people": "Human Resources",
    "engineering": "Research & Development",
    "finance": "Research & Development",
    "operations": "Research & Development",
    "marketing": "Sales",
}


def normalize_department(value: object) -> str:
    department = " ".join(str(value).split()).strip()
    normalized = DEPARTMENT_ALIASES.get(department.casefold(), department)
    if normalized not in DEPARTMENTS:
        return department
    return normalized