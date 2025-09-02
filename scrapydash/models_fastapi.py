# coding: utf-8
"""
FastAPI SQLAlchemy models for ScrapydWeb
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

class Metadata(Base):
    __tablename__ = 'metadata'
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Metadata {self.version}>'

class Task(Base):
    __tablename__ = 'task'
    
    id = Column(Integer, primary_key=True, index=True)
    node = Column(Integer, nullable=False)
    project = Column(String(200), nullable=False)
    version = Column(String(200))
    spider = Column(String(200), nullable=False)
    jobid = Column(String(200))
    settings = Column(Text)
    selected_nodes = Column(Text)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    results = relationship("TaskResult", back_populates="task")
    job_results = relationship("TaskJobResult", back_populates="task")
    
    def __repr__(self):
        return f'<Task {self.id}: {self.project}/{self.spider}>'

class TaskResult(Base):
    __tablename__ = 'taskresult'
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
    node = Column(Integer, nullable=False)
    status = Column(String(50))
    result = Column(Text)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="results")
    
    def __repr__(self):
        return f'<TaskResult {self.id}: task={self.task_id}, node={self.node}>'

class TaskJobResult(Base):
    __tablename__ = 'taskjobresult'
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
    node = Column(Integer, nullable=False)
    jobid = Column(String(200))
    status = Column(String(50))
    result = Column(Text)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="job_results")
    
    def __repr__(self):
        return f'<TaskJobResult {self.id}: task={self.task_id}, jobid={self.jobid}>'

# Dynamic Job table creation function
def create_job_table(node_id: int):
    """Create a dynamic Job table for a specific node"""
    from sqlalchemy import Table, MetaData
    
    table_name = f'job_{node_id}'
    
    job_table = Table(
        table_name, Base.metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('project', String(200), nullable=False),
        Column('spider', String(200), nullable=False),
        Column('jobid', String(200), nullable=False, unique=True),
        Column('start_time', DateTime),
        Column('end_time', DateTime),
        Column('status', String(50)),
        Column('log_url', String(500)),
        Column('items_url', String(500)),
        Column('create_time', DateTime, default=datetime.utcnow),
        Column('update_time', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        extend_existing=True
    )
    
    return job_table
