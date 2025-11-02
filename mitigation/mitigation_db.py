"""Database/storage for mitigation plans."""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from mitigation.action_items import MitigationPlan, ActionItem, Status, Priority


class MitigationDB:
    """Manage mitigation plans storage."""
    
    def __init__(self, storage_path: str = "mitigation_plans.json"):
        """Initialize mitigation database.
        
        Args:
            storage_path: Path to JSON storage file
        """
        self.storage_path = storage_path
        self.plans: Dict[str, MitigationPlan] = {}
        self._load()
    
    def _load(self):
        """Load plans from storage."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.plans = {
                        plan_id: MitigationPlan.from_dict(plan_data)
                        for plan_id, plan_data in data.items()
                    }
            except Exception as e:
                print(f"Error loading mitigation plans: {e}")
                self.plans = {}
        else:
            self.plans = {}
    
    def _save(self):
        """Save plans to storage."""
        try:
            data = {
                plan_id: plan.to_dict()
                for plan_id, plan in self.plans.items()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving mitigation plans: {e}")
    
    def create_plan(self, metric: str, team: str, description: str,
                    current_value: float, target_value: float) -> MitigationPlan:
        """Create a new mitigation plan.
        
        Args:
            metric: Metric name
            team: Team name
            description: Plan description
            current_value: Current metric value
            target_value: Target metric value
            
        Returns:
            Created mitigation plan
        """
        plan_id = str(uuid.uuid4())
        plan = MitigationPlan(
            id=plan_id,
            metric=metric,
            team=team,
            description=description,
            current_value=current_value,
            target_value=target_value
        )
        self.plans[plan_id] = plan
        self._save()
        return plan
    
    def get_plan(self, plan_id: str) -> Optional[MitigationPlan]:
        """Get mitigation plan by ID.
        
        Args:
            plan_id: Plan ID
            
        Returns:
            Mitigation plan or None
        """
        return self.plans.get(plan_id)
    
    def get_plans_by_metric(self, metric: str) -> List[MitigationPlan]:
        """Get all plans for a metric.
        
        Args:
            metric: Metric name
            
        Returns:
            List of mitigation plans
        """
        return [plan for plan in self.plans.values() if plan.metric == metric]
    
    def get_plans_by_team(self, team: str) -> List[MitigationPlan]:
        """Get all plans for a team.
        
        Args:
            team: Team name
            
        Returns:
            List of mitigation plans
        """
        return [plan for plan in self.plans.values() if plan.team == team]
    
    def update_plan(self, plan_id: str, **kwargs) -> Optional[MitigationPlan]:
        """Update mitigation plan.
        
        Args:
            plan_id: Plan ID
            **kwargs: Fields to update
            
        Returns:
            Updated plan or None
        """
        plan = self.plans.get(plan_id)
        if not plan:
            return None
        
        for key, value in kwargs.items():
            if hasattr(plan, key):
                setattr(plan, key, value)
        
        plan.updated_at = datetime.utcnow()
        self._save()
        return plan
    
    def delete_plan(self, plan_id: str) -> bool:
        """Delete mitigation plan.
        
        Args:
            plan_id: Plan ID
            
        Returns:
            True if deleted, False if not found
        """
        if plan_id in self.plans:
            del self.plans[plan_id]
            self._save()
            return True
        return False
    
    def add_action_item(self, plan_id: str, title: str, description: str,
                       priority: Priority = Priority.MEDIUM,
                       assigned_to: str = "", due_date: Optional[datetime] = None) -> Optional[ActionItem]:
        """Add action item to a plan.
        
        Args:
            plan_id: Plan ID
            title: Action item title
            description: Action item description
            priority: Priority level
            assigned_to: Assigned person
            due_date: Due date
            
        Returns:
            Created action item or None
        """
        plan = self.plans.get(plan_id)
        if not plan:
            return None
        
        action_item = ActionItem(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            metric=plan.metric,
            team=plan.team,
            priority=priority,
            assigned_to=assigned_to,
            due_date=due_date
        )
        
        plan.add_action_item(action_item)
        self._save()
        return action_item
    
    def update_action_item(self, plan_id: str, item_id: str, **kwargs) -> Optional[ActionItem]:
        """Update action item.
        
        Args:
            plan_id: Plan ID
            item_id: Action item ID
            **kwargs: Fields to update
            
        Returns:
            Updated action item or None
        """
        plan = self.plans.get(plan_id)
        if not plan:
            return None
        
        action_item = next((item for item in plan.action_items if item.id == item_id), None)
        if not action_item:
            return None
        
        for key, value in kwargs.items():
            if hasattr(action_item, key):
                setattr(action_item, key, value)
        
        action_item.updated_at = datetime.utcnow()
        plan.updated_at = datetime.utcnow()
        self._save()
        return action_item
    
    def delete_action_item(self, plan_id: str, item_id: str) -> bool:
        """Delete action item.
        
        Args:
            plan_id: Plan ID
            item_id: Action item ID
            
        Returns:
            True if deleted, False if not found
        """
        plan = self.plans.get(plan_id)
        if not plan:
            return False
        
        plan.remove_action_item(item_id)
        self._save()
        return True
    
    def get_all_plans(self) -> List[MitigationPlan]:
        """Get all mitigation plans.
        
        Returns:
            List of all plans
        """
        return list(self.plans.values())
    
    def search_plans(self, query: str) -> List[MitigationPlan]:
        """Search plans by query string.
        
        Args:
            query: Search query
            
        Returns:
            List of matching plans
        """
        query_lower = query.lower()
        results = []
        
        for plan in self.plans.values():
            if (query_lower in plan.metric.lower() or
                query_lower in plan.team.lower() or
                query_lower in plan.description.lower()):
                results.append(plan)
        
        return results

