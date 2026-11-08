from enum import Enum as PyEnum


class TypeComponent(str, PyEnum):
    PC1 = "PC1"
    REPORT = "Reporte"
    CARRIER = "Carrier"
    API = "API"
    BATCH = "Batch"
    SECURITY = "Seguridad"
    OTHER = "other"
