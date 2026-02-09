"""
Event publishing module for Dapr Pub/Sub integration.
T-012: Create events module init in api/src/events/__init__.py
Plan ref: Plan §4.1 (new files), §4.2 (module exports)
Constitution VII: All event publishing via Dapr, no direct Kafka clients
"""
from .publisher import EventPublisher, get_event_publisher
from .schemas import CloudEvent, TaskEventData, SyncEventData, ReminderEventData

__all__ = [
    "EventPublisher",
    "get_event_publisher",
    "CloudEvent",
    "TaskEventData",
    "SyncEventData",
    "ReminderEventData",
]
