from sqlalchemy import Column, Integer, Float, String
from app.storage import Base

class Alert(Base):

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    src_ip = Column(String)
    dst_ip = Column(String)
    score = Column(Float)