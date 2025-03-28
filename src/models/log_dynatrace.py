from pydantic import BaseModel
from datetime import datetime

class LogDynatrace(BaseModel):
    """Model for Dynatrace log query configuration"""
    
    query: str
    default_timeframe_start: datetime
    default_timeframe_end: datetime
    timezone: str
    locale: str
    max_result_records: int
    max_result_bytes: int
    fetch_timeout_seconds: int
    request_timeout_milliseconds: int
    enable_preview: bool
    default_sampling_ratio: int
    default_scan_limit_gbytes: int

    class Config:
        """Pydantic model configuration"""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "query": "fetch logs | filter matchesValue(dt.entity.process_group, \"PROCESS_GROUP-A6835EC7482B0471\")",
                "default_timeframe_start": "2024-01-01T12:10:04.123Z",
                "default_timeframe_end": "2024-01-20T13:10:04.123Z",
                "timezone": "UTC",
                "locale": "en_US",
                "max_result_records": 1000,
                "max_result_bytes": 1000000,
                "fetch_timeout_seconds": 60,
                "request_timeout_milliseconds": 1000,
                "enable_preview": True,
                "default_sampling_ratio": 1000,
                "default_scan_limit_gbytes": 100
            }
        }