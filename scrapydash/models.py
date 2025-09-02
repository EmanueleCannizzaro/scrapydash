# coding: utf-8
import os
from pprint import pformat
import time
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from .vars import STATE_RUNNING

# Legacy SQLAlchemy compatibility class
class LegacySQLAlchemy:
    """Legacy SQLAlchemy class for backward compatibility"""
    def __init__(self, session_options=None):
        self.session_options = session_options or {}
        self.Base = declarative_base()
        self.engine = create_engine('sqlite:///scrapydweb.db')  # Replace with your database URL
        self.Base.metadata.bind = self.engine
        self.Session = sessionmaker(bind=self.engine, **self.session_options)
        self.session = self.Session()
        
        # Legacy Flask app compatibility
        self.app = LegacyFlaskApp()
    
    def create_all(self, app=None):
        """Legacy create_all method"""
        try:
            self.Base.metadata.create_all(self.engine)
        except Exception as e:
            print(f"Error creating database tables: {e}")
    
    def drop_all(self, app=None):
        """Legacy drop_all method"""
        self.Base.metadata.drop_all(self.engine)

class LegacyQuery:
    """Legacy Query class for Flask-SQLAlchemy compatibility"""
    def __init__(self, model_class, session):
        self.model_class = model_class
        self.session = session
    
    def filter_by(self, **kwargs):
        return self.session.query(self.model_class).filter_by(**kwargs)
    
    def first(self):
        return self.session.query(self.model_class).first()
    
    def all(self):
        return self.session.query(self.model_class).all()

class LegacyFlaskApp:
    """Legacy Flask app for backward compatibility"""
    def __init__(self):
        self.config = {}
    
    def app_context(self):
        """Legacy app_context for backward compatibility"""
        return LegacyAppContext()

class LegacyAppContext:
    """Legacy app context manager for backward compatibility"""
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


db = LegacySQLAlchemy(session_options=dict(autocommit=False, autoflush=True))
db.create_all()


# TODO: Database Migrations https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
# http://flask-sqlalchemy.pocoo.org/2.3/binds/#binds
class Metadata(db.Base):
    __tablename__ = 'metadata'
    __bind_key__ = 'metadata'

    id = Column(Integer, primary_key=True)
    version = Column(String(20), unique=True, nullable=False)
    last_check_update_timestamp = Column(Float, unique=False, default=time.time)
    main_pid = Column(Integer, unique=False, nullable=True)
    logparser_pid = Column(Integer, unique=False, nullable=True)
    poll_pid = Column(Integer, unique=False, nullable=True)
    pageview = Column(Integer, unique=False, nullable=False, default=0)
    url_scrapydweb = Column(Text(), unique=False, nullable=False, default='http://127.0.0.1:5000')
    url_jobs = Column(String(255), unique=False, nullable=False, default='/1/jobs/')
    url_schedule_task = Column(String(255), unique=False, nullable=False, default='/1/schedule/task/')
    url_delete_task_result = Column(String(255), unique=False, nullable=False, default='/1/tasks/xhr/delete/1/1/')
    username = Column(String(255), unique=False, nullable=True)
    password = Column(String(255), unique=False, nullable=True)
    scheduler_state = Column(Integer, unique=False, nullable=False, default=STATE_RUNNING)
    jobs_per_page = Column(Integer, unique=False, nullable=False, default=100)
    tasks_per_page = Column(Integer, unique=False, nullable=False, default=100)
    jobs_style = Column(String(8), unique=False, nullable=False, default='database')  # 'classic'

    def __repr__(self):
        return pformat(vars(self))

# Add query property to Metadata class for Flask-SQLAlchemy compatibility
Metadata.query = LegacyQuery(Metadata, db.session)


# TODO: Timezone Conversions https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xii-dates-and-times
def create_jobs_table(server):
    class Job(db.Base):
        __tablename__ = server
        __bind_key__ = 'jobs'
        # https://stackoverflow.com/questions/10059345/sqlalchemy-unique-across-multiple-columns
        # https://stackoverflow.com/questions/43975349/why-uniqueconstraint-doesnt-work-in-flask-sqlalchemy
        __table_args__ = (UniqueConstraint('project', 'spider', 'job'), )

        id = Column(Integer, primary_key=True)
        project = Column(String(255), unique=False, nullable=False)  # Pending
        spider = Column(String(255), unique=False, nullable=False)  # Pending
        job = Column(String(255), unique=False, nullable=False)  # Pending
        status = Column(String(1), unique=False, nullable=False, index=True)  # Pending 0, Running 1, Finished 2
        deleted = Column(String(1), unique=False, nullable=False, default='0', index=True)
        create_time = Column(DateTime, unique=False, nullable=False, default=datetime.now)
        update_time = Column(DateTime, unique=False, nullable=False, default=datetime.now)

        pages = Column(Integer, unique=False, nullable=True)
        items = Column(Integer, unique=False, nullable=True)
        pid = Column(Integer, unique=False, nullable=True)  # Running
        start = Column(DateTime, unique=False, nullable=True, index=True)
        runtime = Column(String(20), unique=False, nullable=True)
        finish = Column(DateTime, unique=False, nullable=True, index=True)  # Finished
        href_log = Column(Text(), unique=False, nullable=True)
        href_items = Column(Text(), unique=False, nullable=True)

        def __repr__(self):
            return "<Job #%s in table %s, %s/%s/%s start: %s>" % (
                self.id, self.__tablename__, self.project, self.spider, self.job, self.start)

    return Job
    # sqlalchemy/ext/declarative/clsregistry.py:128: SAWarning: This declarative base already contains a class
    # with the same class name and module name as scrapydweb.models.Job,
    # and will be replaced in the string-lookup table.
    # https://stackoverflow.com/questions/27773489/dynamically-create-a-python-subclass-in-a-function
    # return type('Job_%s' % server, (Job, ), dict(__tablename__=server,  __bind_key__='jobs'))

# print(dir([create_table(s) for s in 'abc'][0]))


# http://flask-sqlalchemy.pocoo.org/2.3/models/    One-to-Many Relationships
# https://techarena51.com/blog/one-to-many-relationships-with-flask-sqlalchemy/
# https://docs.sqlalchemy.org/en/latest/orm/cascades.html#delete-orphan
# https://docs.sqlalchemy.org/en/latest/core/constraints.html#indexes
# https://stackoverflow.com/questions/14419299/adding-indexes-to-sqlalchemy-models-after-table-creation
# https://stackoverflow.com/questions/8890738/sqlalchemy-does-column-with-foreignkey-creates-index-automatically
class Task(db.Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=False, nullable=True)  # None
    trigger = Column(String(8), unique=False, nullable=False)  # cron, interval, date
    create_time = Column(DateTime, unique=False, nullable=False, default=datetime.now)  # datetime.utcnow
    update_time = Column(DateTime, unique=False, nullable=False, default=datetime.now)

    project = Column(String(255), unique=False, nullable=False)
    version = Column(String(255), unique=False, nullable=False)
    spider = Column(String(255), unique=False, nullable=False)
    jobid = Column(String(255), unique=False, nullable=False)
    settings_arguments = Column(Text(), unique=False, nullable=False)
    selected_nodes = Column(Text(), unique=False, nullable=False)

    year = Column(String(255), unique=False, nullable=False)
    month = Column(String(255), unique=False, nullable=False)
    day = Column(String(255), unique=False, nullable=False)
    week = Column(String(255), unique=False, nullable=False)
    day_of_week = Column(String(255), unique=False, nullable=False)
    hour = Column(String(255), unique=False, nullable=False)
    minute = Column(String(255), unique=False, nullable=False)
    second = Column(String(255), unique=False, nullable=False)

    start_date = Column(String(19), unique=False, nullable=True)  # '2019-01-01 00:00:01'     None
    end_date = Column(String(19), unique=False, nullable=True)  # '2019-01-01 00:00:01'       None

    timezone = Column(String(255), unique=False, nullable=True)  # None
    jitter = Column(Integer, unique=False, nullable=False)  # int
    misfire_grace_time = Column(Integer, unique=False, nullable=True)  # None|a positive integer
    coalesce = Column(String(5), unique=False, nullable=False)  # 'True'|'False'
    max_instances = Column(Integer, unique=False, nullable=False)  # int

    results = relationship('TaskResult', backref='task', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return "<Task #%s (%s), %s/%s/%s/%s, created at %s, updated at %s>" % (
                self.id, self.name, self.project, self.version, self.spider, self.jobid,
                self.create_time, self.update_time)


class TaskResult(db.Base):
    __tablename__ = 'task_result'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'), nullable=False, index=True)
    execute_time = Column(DateTime, unique=False, nullable=False, default=datetime.now)
    fail_count = Column(Integer, unique=False, nullable=False, default=0)
    pass_count = Column(Integer, unique=False, nullable=False, default=0)

    results = relationship('TaskJobResult', backref='task_result', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return "<TaskResult #%s of task #%s (%s), [FAIL %s, PASS %s], executed at %s>" % (
                self.id, self.task_id, self.task.name, self.fail_count, self.pass_count, self.execute_time)


class TaskJobResult(db.Base):
    __tablename__ = 'task_job_result'

    id = Column(Integer, primary_key=True)
    task_result_id = Column(Integer, ForeignKey('task_result.id'), nullable=False, index=True)
    run_time = Column(DateTime, unique=False, nullable=False, default=datetime.now)
    node = Column(Integer, unique=False, nullable=False, index=True)
    server = Column(String(255), unique=False, nullable=False)  # '127.0.0.1:6800'
    status_code = Column(Integer, unique=False, nullable=False)  # -1, 200
    status = Column(String(9), unique=False, nullable=False)  # ok|error|exception
    # psycopg2.DataError) value too long for type character varying(1000)
    # https://docs.sqlalchemy.org/en/latest/core/type_basics.html#sqlalchemy.types.Text
    # In general, TEXT objects do not have a length
    result = Column(Text(), unique=False, nullable=False)  # jobid|message|exception

    def __repr__(self):
        kwargs = dict(
            task_id=self.task_result.task_id,
            task_name=self.task_result.task.name,
            project=self.task_result.task.project,
            version=self.task_result.task.version,
            spider=self.task_result.task.spider,
            jobid=self.task_result.task.jobid,
            run_time=str(self.run_time),  # TypeError: Object of type datetime is not JSON serializable
            node=self.node,
            server=self.server,
            status_code=self.status_code,
            status=self.status,
            result=self.result,
            task_result_id=self.task_result_id,
            id=self.id,
        )
        return '<TaskJobResult \n%s>' % pformat(kwargs, indent=4)
