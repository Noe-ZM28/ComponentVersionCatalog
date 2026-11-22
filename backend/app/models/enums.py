from enum import Enum as PyEnum


class TypeComponent(str, PyEnum):
    DIALOGUE        = "Dialogue"
    VARIABLE        = "Variable"
    SCRIPT          = "Script"
    RECURRING_JOB   = "Recurring Job"
