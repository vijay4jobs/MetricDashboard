"""Mitigation plan and action item management."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class Priority(Enum):
    """Action item priority levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Status(Enum):
    """Action item status."""
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    BLOCKED = "Blocked"
    CANCELLED = "Cancelled"


@dataclass
class ActionItem:
    """Represents a single action item."""
    id: str
    title: str
    description: str
    metric: str
    team: str
    priority: Priority = Priority.MEDIUM
    status: Status = Status.TODO
    assigned_to: str = ""
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'metric': self.metric,
            'team': self.team,
            'priority': self.priority.value,
            'status': self.status.value,
            'assigned_to': self.assigned_to,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': self.tags,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionItem':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            metric=data['metric'],
            team=data['team'],
            priority=Priority(data.get('priority', 'Medium')),
            status=Status(data.get('status', 'To Do')),
            assigned_to=data.get('assigned_to', ''),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            created_at=datetime.fromisoformat(data.get('created_at', datetime.utcnow().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.utcnow().isoformat())),
            tags=data.get('tags', []),
            notes=data.get('notes', '')
        )


@dataclass
class MitigationPlan:
    """Represents a mitigation plan for a metric."""
    id: str
    metric: str
    team: str
    description: str
    current_value: float
    target_value: float
    action_items: List[ActionItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_action_item(self, action_item: ActionItem):
        """Add an action item to the plan."""
        self.action_items.append(action_item)
        self.updated_at = datetime.utcnow()
    
    def remove_action_item(self, action_item_id: str):
        """Remove an action item by ID."""
        self.action_items = [item for item in self.action_items if item.id != action_item_id]
        self.updated_at = datetime.utcnow()
    
    def get_progress(self) -> Dict[str, Any]:
        """Get mitigation plan progress."""
        total = len(self.action_items)
        if total == 0:
            return {'percentage': 0, 'completed': 0, 'total': 0}
        
        completed = sum(1 for item in self.action_items if item.status == Status.DONE)
        percentage = (completed / total) * 100
        
        return {
            'percentage': round(percentage, 2),
            'completed': completed,
            'total': total,
            'in_progress': sum(1 for item in self.action_items if item.status == Status.IN_PROGRESS),
            'todo': sum(1 for item in self.action_items if item.status == Status.TODO)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'metric': self.metric,
            'team': self.team,
            'description': self.description,
            'current_value': self.current_value,
            'target_value': self.target_value,
            'action_items': [item.to_dict() for item in self.action_items],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MitigationPlan':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            metric=data['metric'],
            team=data['team'],
            description=data['description'],
            current_value=data['current_value'],
            target_value=data['target_value'],
            action_items=[ActionItem.from_dict(item) for item in data.get('action_items', [])],
            created_at=datetime.fromisoformat(data.get('created_at', datetime.utcnow().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.utcnow().isoformat()))
        )

