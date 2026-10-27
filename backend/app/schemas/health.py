from datetime import datetime
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Application health status")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Current deployment environment")
    database_status: str = Field(..., description="Database connection status")
    timestamp: datetime = Field(..., description="Timestamp of the health check")
