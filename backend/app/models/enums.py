from enum import Enum as PyEnum


class TypeComponent(str, PyEnum):
    DIALOGUE        = "Dialogue"
    VARIABLE        = "Variable"
    SCRIPT          = "Script"
    RECURRING_JOB   = "Recurring Job"
    CHAIN           = "Chain"
    MAPPING         = "Mapping"
    FILE_DEFINITION = "File Definition"
    XML             = "XML"
    SORTING         = "Sorting"
    SPLIT           = "Split"
    DICTIONARY      = "Dictionary"

    OTHER = "other"
