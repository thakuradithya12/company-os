"""SQLAlchemy persistence models registered with the shared metadata."""

from company_os.db.models.task import TaskAuditEventRecord, TaskRecord

__all__ = ["TaskAuditEventRecord", "TaskRecord"]
