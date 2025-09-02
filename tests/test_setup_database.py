# coding: utf-8
"""
Tests for setup_database utility functions
"""
import os
import tempfile
import shutil
import pytest

from scrapydash.utils.setup_database import (
    parse_database_url_pattern,
    setup_database,
    PATTERN_MYSQL,
    PATTERN_POSTGRESQL, 
    PATTERN_SQLITE,
    DB_APSCHEDULER,
    DB_TIMERTASKS,
    DB_METADATA,
    DB_JOBS,
    DBS
)


def test_database_constants():
    """Test database constants are defined"""
    assert DB_APSCHEDULER == 'scrapydash_apscheduler'
    assert DB_TIMERTASKS == 'scrapydash_timertasks' 
    assert DB_METADATA == 'scrapydash_metadata'
    assert DB_JOBS == 'scrapydash_jobs'
    assert len(DBS) == 4
    assert all(db in DBS for db in [DB_APSCHEDULER, DB_TIMERTASKS, DB_METADATA, DB_JOBS])


def test_regex_patterns():
    """Test regex patterns for database URLs"""
    # Test MySQL pattern
    mysql_url = "mysql://user:pass@localhost:3306"
    mysql_match = PATTERN_MYSQL.match(mysql_url)
    assert mysql_match is not None
    assert mysql_match.groups() == ('user', 'pass', 'localhost', '3306')
    
    mysql_url_no_pass = "mysql://user@localhost:3306"
    mysql_match_no_pass = PATTERN_MYSQL.match(mysql_url_no_pass)
    assert mysql_match_no_pass is not None
    assert mysql_match_no_pass.groups() == ('user', None, 'localhost', '3306')
    
    # Test PostgreSQL pattern
    postgres_url = "postgresql://user:pass@localhost:5432"
    postgres_match = PATTERN_POSTGRESQL.match(postgres_url)
    assert postgres_match is not None
    assert postgres_match.groups() == ('user', 'pass', 'localhost', '5432')
    
    postgres_url2 = "postgres://user@localhost:5432"
    postgres_match2 = PATTERN_POSTGRESQL.match(postgres_url2)
    assert postgres_match2 is not None
    assert postgres_match2.groups() == ('user', None, 'localhost', '5432')
    
    # Test SQLite pattern
    sqlite_url = "sqlite:///path/to/database.db"
    sqlite_match = PATTERN_SQLITE.match(sqlite_url)
    assert sqlite_match is not None
    assert sqlite_match.groups() == ('path/to/database.db',)


def test_database_url_pattern_function():
    """Test parse_database_url_pattern function"""
    # Test MySQL
    mysql_url = "mysql://user:pass@localhost:3306"
    m_mysql, m_postgres, m_sqlite = parse_database_url_pattern(mysql_url)
    assert m_mysql is not None
    assert m_postgres is None
    assert m_sqlite is None
    
    # Test PostgreSQL
    postgres_url = "postgresql://user:pass@localhost:5432"
    m_mysql, m_postgres, m_sqlite = parse_database_url_pattern(postgres_url)
    assert m_mysql is None
    assert m_postgres is not None
    assert m_sqlite is None
    
    # Test SQLite
    sqlite_url = "sqlite:///path/to/db.db"
    m_mysql, m_postgres, m_sqlite = parse_database_url_pattern(sqlite_url)
    assert m_mysql is None
    assert m_postgres is None
    assert m_sqlite is not None
    
    # Test invalid URL
    invalid_url = "invalid://something"
    m_mysql, m_postgres, m_sqlite = parse_database_url_pattern(invalid_url)
    assert m_mysql is None
    assert m_postgres is None
    assert m_sqlite is None


def test_setup_database_sqlite():
    """Test setup_database with SQLite"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Test with path only (no URL match)
        db_path = os.path.join(tmp_dir, 'test_db')
        setup_database("invalid://url", db_path) 
        assert os.path.isdir(db_path)


def test_setup_database_path_normalization():
    """Test path normalization in setup_database"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Test with backslashes and trailing slashes
        db_path = os.path.join(tmp_dir, 'test_db') + "/"
        db_path_with_backslashes = db_path.replace('/', '\\')
        
        setup_database("invalid://url", db_path_with_backslashes)
        # Should create directory even with path normalization
        expected_path = db_path.rstrip('/')
        assert os.path.isdir(expected_path)


class TestDatabaseSetupIntegration:
    """Integration tests for database setup"""
    
    def test_sqlite_path_creation(self):
        """Test SQLite database directory creation"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_dir = os.path.join(tmp_dir, 'sqlite') 
            sqlite_url = f"sqlite:///{db_dir}"
            
            assert not os.path.exists(db_dir)
            setup_database(sqlite_url, "unused_fallback")
            assert os.path.isdir(db_dir)
    
    @pytest.mark.skip(reason="setup_mysql tries to import pymysql and exits on failure")
    def test_non_sqlite_urls_dont_create_dirs(self):
        """Test that MySQL/PostgreSQL URLs don't create local directories"""
        # This test is skipped because setup_mysql tries to actually setup MySQL
        pass