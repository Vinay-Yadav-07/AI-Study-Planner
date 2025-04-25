import json
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="study_planner.json"):
        self.db_path = db_path
        self.data = self._load_data()
    
    def _load_data(self):
        """Load data from the JSON file if it exists"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._create_empty_db()
        else:
            return self._create_empty_db()
    
    def _create_empty_db(self):
        """Create an empty database structure"""
        return {
            "plans": [],
            "progress": {},
            "calendar_events": [],
            "user_preferences": {}
        }
    
    def _save_data(self):
        """Save data to the JSON file"""
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_plans(self):
        """Get all study plans"""
        return self.data["plans"]
    
    def get_plan(self, plan_id):
        """Get a specific study plan by ID"""
        for plan in self.data["plans"]:
            if plan["id"] == plan_id:
                return plan
        return None
    
    def add_plan(self, plan):
        """Add a new study plan"""
        self.data["plans"].append(plan)
        self._save_data()
        return plan["id"]
    
    def update_plan(self, plan_id, updated_plan):
        """Update an existing study plan"""
        for i, plan in enumerate(self.data["plans"]):
            if plan["id"] == plan_id:
                self.data["plans"][i] = updated_plan
                self._save_data()
                return True
        return False
    
    def delete_plan(self, plan_id):
        """Delete a study plan"""
        for i, plan in enumerate(self.data["plans"]):
            if plan["id"] == plan_id:
                del self.data["plans"][i]
                if plan_id in self.data["progress"]:
                    del self.data["progress"][plan_id]
                self._save_data()
                return True
        return False
    
    def get_progress(self, plan_id):
        """Get progress for a specific plan"""
        return self.data["progress"].get(plan_id, {
            "completed_tasks": [],
            "total_tasks": 0,
            "completion_percentage": 0
        })
    
    def update_progress(self, plan_id, progress):
        """Update progress for a specific plan"""
        self.data["progress"][plan_id] = progress
        self._save_data()
    
    def get_calendar_events(self):
        """Get all calendar events"""
        return self.data["calendar_events"]
    
    def add_calendar_event(self, event):
        """Add a new calendar event"""
        self.data["calendar_events"].append(event)
        self._save_data()
        return event["id"]
    
    def delete_calendar_event(self, event_id):
        """Delete a calendar event"""
        for i, event in enumerate(self.data["calendar_events"]):
            if event["id"] == event_id:
                del self.data["calendar_events"][i]
                self._save_data()
                return True
        return False
    
    def get_user_preferences(self):
        """Get user preferences"""
        return self.data["user_preferences"]
    
    def update_user_preferences(self, preferences):
        """Update user preferences"""
        self.data["user_preferences"] = preferences
        self._save_data()
    
    def clear_all_data(self):
        """Clear all data"""
        self.data = self._create_empty_db()
        self._save_data()
