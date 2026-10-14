from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from database import Base

class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    motion = Column(Boolean, default=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)