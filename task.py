import csv
import json
from datetime import datetime
from pathlib import Path
from crypto import CryptoManager

# Các class dữ liệu

class Task:
    def __init__(self, name: str):
        self.name = name
        self.create_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    def to_dict(self):
        return {"name":self.name, "create_time":self.create_time}

class ToDoTask(Task):
    def __init__(self, name: str, priority: str, description: str, deadline: str, status: str = "[ ]"):
        super().__init__(name)
        self.priority = priority
        self.description = description
        self.deadline = deadline
        self.status = status
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "priority": self.priority,
            "description": self.description,
            "deadline": self.deadline,
            "status": self.status,
        })
        return data
    
class RecurringTask(Task):
    def __init__(self, name: str, description: str, recur_type: str, time_of_recur: str, status:str = "[ ]"):
        super().__init__(name)
        self.description = description
        self.recur_type = recur_type
        self.time_of_recur = time_of_recur
        self.status = status
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "recur_type": self.recur_type,
            "description": self.description,
            "time_of_recur": self.time_of_recur,
            "status": self.status,
        })
        return data

class Journal(Task):
    def __init(self, name:str, content:str, mood:str):
        date_name = name if name else datetime.now().strftime("%d-%m-%Y")
        super().__init__(date_name)
        self.mood = mood
        self.content = content

# Class quản lý toàn bộ logic với file CSV

class TaskManager:
    def __init__(self, username:str, crypto:CryptoManager):
        self.username = username
        self.crypto = crypto

        self.todo_file = Path(f"database/{self.username}_todo.csv")
        self.recurring_file = Path(f"database/{self.username}_recurring.csv")
        self.journal_file = Path(f"database/{self.username}_todo.csv")

print(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

ta = ToDoTask("hello", "high", "Very good", "nah")
print(ta.create_time)