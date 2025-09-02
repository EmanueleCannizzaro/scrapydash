# coding: utf-8
"""
FastAPI scheduler module for ScrapydWeb
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import logging

logger = logging.getLogger(__name__)

class SchedulerManager:
    """Scheduler manager for FastAPI"""
    
    def __init__(self):
        self.scheduler = None
        self._started = False
    
    def start(self):
        """Start the scheduler"""
        if self._started:
            return
            
        try:
            self.scheduler = BackgroundScheduler()
            
            # Add event listeners
            self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
            self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
            
            self.scheduler.start()
            self._started = True
            logger.info("Scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler and self._started:
            try:
                self.scheduler.shutdown()
                self._started = False
                logger.info("Scheduler stopped")
            except Exception as e:
                logger.error(f"Error stopping scheduler: {e}")
    
    def _job_executed(self, event):
        """Handle job execution events"""
        logger.info(f"Job {event.job_id} executed successfully")
    
    def _job_error(self, event):
        """Handle job error events"""
        logger.error(f"Job {event.job_id} failed: {event.exception}")
    
    def add_job(self, func, trigger, **kwargs):
        """Add a job to the scheduler"""
        if self.scheduler:
            return self.scheduler.add_job(func, trigger, **kwargs)
    
    def remove_job(self, job_id):
        """Remove a job from the scheduler"""
        if self.scheduler:
            self.scheduler.remove_job(job_id)

# Global scheduler manager instance
scheduler_manager = SchedulerManager()
