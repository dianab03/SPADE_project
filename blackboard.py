import asyncio

class Blackboard:
    def __init__(self):
        self.tasks = {}
        self.lock = asyncio.Lock()

    async def add_task(self, task_id, task_data):
        async with self.lock:
            self.tasks[task_id] = task_data

    async def get_task(self, task_id):
        async with self.lock:
            return self.tasks.get(task_id)
        
    async def take_task(self, task_type):
        async with self.lock:
            for task_id, task_data in self.tasks.items():
                if task_data.get("status") == "new" and task_data.get("type") == task_type:
                    task_data["status"] = "in_progress"
                    return task_id, task_data
            return None, None
    
    async def complete_task(self, task_id, result):
        async with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]["status"] = "completed"
                self.tasks[task_id]["result"] = result