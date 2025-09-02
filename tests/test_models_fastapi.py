# coding: utf-8
"""
Tests for FastAPI SQLAlchemy models
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scrapydash.database import Base
from scrapydash.models_fastapi import Metadata, Task, TaskResult, TaskJobResult, create_job_table


@pytest.fixture
def db_session():
    """Create test database session"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_metadata_model(db_session):
    """Test Metadata model creation and operations"""
    metadata = Metadata(version="1.0.0")
    
    assert metadata.version == "1.0.0"
    assert metadata.id is None  # Not yet saved
    
    db_session.add(metadata)
    db_session.commit()
    
    assert metadata.id is not None
    assert metadata.created_at is not None
    assert metadata.updated_at is not None
    assert repr(metadata) == "<Metadata 1.0.0>"


def test_task_model(db_session):
    """Test Task model creation and operations"""
    task = Task(
        node=1,
        project="test_project", 
        spider="test_spider",
        version="1.0",
        jobid="test_job_123"
    )
    
    assert task.node == 1
    assert task.project == "test_project"
    assert task.spider == "test_spider"
    assert task.version == "1.0"
    assert task.jobid == "test_job_123"
    
    db_session.add(task)
    db_session.commit()
    
    assert task.id is not None
    assert task.create_time is not None
    assert task.update_time is not None
    assert repr(task) == f"<Task {task.id}: test_project/test_spider>"


def test_task_result_model(db_session):
    """Test TaskResult model creation and operations"""
    # Create a task first
    task = Task(node=1, project="test_project", spider="test_spider")
    db_session.add(task)
    db_session.commit()
    
    # Create task result
    result = TaskResult(
        task_id=task.id,
        node=1,
        status="completed",
        result="success"
    )
    
    assert result.task_id == task.id
    assert result.node == 1
    assert result.status == "completed"
    assert result.result == "success"
    
    db_session.add(result)
    db_session.commit()
    
    assert result.id is not None
    assert result.create_time is not None
    assert result.update_time is not None
    assert repr(result) == f"<TaskResult {result.id}: task={task.id}, node=1>"


def test_task_job_result_model(db_session):
    """Test TaskJobResult model creation and operations"""
    # Create a task first
    task = Task(node=1, project="test_project", spider="test_spider")
    db_session.add(task)
    db_session.commit()
    
    # Create task job result
    job_result = TaskJobResult(
        task_id=task.id,
        node=1,
        jobid="job_123",
        status="finished",
        result="success"
    )
    
    assert job_result.task_id == task.id
    assert job_result.node == 1
    assert job_result.jobid == "job_123"
    assert job_result.status == "finished"
    assert job_result.result == "success"
    
    db_session.add(job_result)
    db_session.commit()
    
    assert job_result.id is not None
    assert job_result.create_time is not None
    assert job_result.update_time is not None
    assert repr(job_result) == f"<TaskJobResult {job_result.id}: task={task.id}, jobid=job_123>"


def test_task_relationships(db_session):
    """Test relationships between Task, TaskResult, and TaskJobResult"""
    # Create task
    task = Task(node=1, project="test_project", spider="test_spider")
    db_session.add(task)
    db_session.commit()
    
    # Create task result
    result = TaskResult(task_id=task.id, node=1, status="completed")
    db_session.add(result)
    
    # Create job result
    job_result = TaskJobResult(task_id=task.id, node=1, jobid="job_123", status="finished")
    db_session.add(job_result)
    
    db_session.commit()
    
    # Test relationships
    assert len(task.results) == 1
    assert len(task.job_results) == 1
    assert task.results[0] == result
    assert task.job_results[0] == job_result
    assert result.task == task
    assert job_result.task == task


def test_create_job_table():
    """Test dynamic job table creation"""
    node_id = 1
    job_table = create_job_table(node_id)
    
    assert job_table.name == f"job_{node_id}"
    assert 'id' in job_table.columns
    assert 'project' in job_table.columns
    assert 'spider' in job_table.columns
    assert 'jobid' in job_table.columns
    assert 'start_time' in job_table.columns
    assert 'end_time' in job_table.columns
    assert 'status' in job_table.columns
    assert 'log_url' in job_table.columns
    assert 'items_url' in job_table.columns
    assert 'create_time' in job_table.columns
    assert 'update_time' in job_table.columns


def test_unique_constraints(db_session):
    """Test unique constraints"""
    # Test Metadata version uniqueness
    metadata1 = Metadata(version="1.0.0")
    metadata2 = Metadata(version="1.0.0")
    
    db_session.add(metadata1)
    db_session.commit()
    
    db_session.add(metadata2)
    with pytest.raises(Exception):  # Should raise integrity error
        db_session.commit()