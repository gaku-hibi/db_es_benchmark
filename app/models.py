from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class EmployeeIndividualMap(Base):
    __tablename__ = 'employee_individual_map'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), nullable=False, unique=True)
    individual_id = Column(String(50), nullable=False, unique=True)
    
    locations = relationship("Location", back_populates="individual")
    
    __table_args__ = (
        Index('idx_employee_id', 'employee_id'),
        Index('idx_individual_id', 'individual_id'),
    )

class Location(Base):
    __tablename__ = 'location'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    individual_id = Column(String(50), ForeignKey('employee_individual_map.individual_id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    
    individual = relationship("EmployeeIndividualMap", back_populates="locations")
    
    __table_args__ = (
        Index('idx_individual_timestamp', 'individual_id', 'timestamp'),
        Index('idx_timestamp', 'timestamp'),
        Index('idx_location', 'longitude', 'latitude'),
    )

def get_db_engine():
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'benchmark_db')
    db_user = os.environ.get('DB_USER', 'benchmark_user')
    db_password = os.environ.get('DB_PASSWORD', 'benchmark_pass')
    
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(connection_string, pool_size=20, max_overflow=0)

def create_tables():
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    return engine

def get_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()