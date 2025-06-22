import asyncio
import time
import uuid
import re
import logging
from spade.behaviour import CyclicBehaviour
from database import Database

# Set up logging
logger = logging.getLogger(__name__)

class PostTaskAndCheckResultBehaviour(CyclicBehaviour):

    def __init__(self, blackboard, queries):
        super().__init__()
        self.blackboard = blackboard
        self.queries = queries
        self.tasks_to_check = {} 

    async def run(self):
        if self.queries:
            query = self.queries.pop(0)
            task_id = str(uuid.uuid4())
            task_data = {"type": query["type"], "data": query["data"], "status": "new"}
            await self.blackboard.add_task(task_id, task_data)
            self.tasks_to_check[task_id] = time.time()
            print(f"CustomerAgent: Posted task {task_id} of type '{query['type']}'")

        completed_tasks = []
        for task_id in self.tasks_to_check:
            task = await self.blackboard.get_task(task_id)
            if task and task.get("status") == "completed":
                print(f"CustomerAgent: Received result for task {task_id}: '{task['result']}'")
                completed_tasks.append(task_id)

        for task_id in completed_tasks:
            del self.tasks_to_check[task_id]

        await asyncio.sleep(2)


class ProcessTaskBehaviour(CyclicBehaviour):
    def __init__(self, blackboard, agent_type):
        super().__init__()
        self.blackboard = blackboard
        self.agent_type = agent_type
        logger.info(f"Initializing database for {agent_type} agent")
        self.db = Database()

    async def run(self):
        task_id, task_data = await self.blackboard.take_task(self.agent_type)
        if task_id and task_data:
            agent_name = self.agent.name.split('@')[0]
            print(f"{agent_name}: Picked up task {task_id}...")
            
            result = await self.process_task(task_data)
            
            await self.blackboard.complete_task(task_id, result)
            print(f"{agent_name}: Completed task {task_id}")
        else:
            await asyncio.sleep(1)

    async def process_task(self, task_data):
        if self.agent_type == "refund":
            match = re.search(r'#(R-\d+)', task_data["data"])
            if not match:
                return "Could not find a valid order number in the request."
            
            order_id = match.group(1)
            logger.info(f"Checking refund eligibility for order {order_id}")
            result = self.db.check_refund_eligibility(order_id)
            logger.info(f"Refund check result: {result}")
            
            if result["eligible"]:
                return (f"Refund approved for order {order_id}. "
                       f"Order details: Date: {result['details']['order_date']}, "
                       f"Amount: ${result['details']['total_amount']:.2f}")
            else:
                return f"Refund denied for order {order_id}. Reason: {result['reason']}"

        elif self.agent_type == "product_issue":
            text = task_data["data"].lower()
            logger.info(f"Processing product issue: {text}")
            
            products = ["toaster", "coffee maker", "blender"]
            found_product = None
            for product in products:
                if product in text:
                    found_product = product
                    break
            
            if not found_product:
                return "Could not identify the product in your message. Please specify the product name."
            
            logger.info(f"Found product: {found_product}")
            
            issues = {
                "not working": "not working",
                "broken": "not working",
                "doesn't work": "not working",
                "leaking": "leaking",
                "leaks": "leaking",
                "not blending": "not blending",
                "won't blend": "not blending"
            }
            
            found_issue = None
            for key, value in issues.items():
                if key in text:
                    found_issue = value
                    break
            
            logger.info(f"Found issue: {found_issue}")
            result = self.db.get_product_solution(found_product, found_issue)
            logger.info(f"Product solution result: {result}")
            
            if result["found"]:
                return f"Here's how to fix your {found_product}:\n{result['solution']}"
            else:
                return (f"I understand you're having an issue with your {found_product}. "
                       "However, I couldn't identify the specific problem. "
                       "Please describe the issue in more detail.")

        elif self.agent_type == "general_request":
            text = task_data["data"].lower()
            logger.info(f"Processing general request: {text}")
            
            if "hours" in text and ("weekend" in text or "saturday" in text or "sunday" in text):
                logger.info("Fetching weekend hours")
                hours = self.db.get_store_info("weekend_hours")
                return f"Our weekend hours are: {hours}"
            
            elif "contact" in text or "email" in text:
                logger.info("Fetching contact information")
                email = self.db.get_store_info("contact_email")
                phone = self.db.get_store_info("phone")
                return f"You can reach us at:\nEmail: {email}\nPhone: {phone}"
            
            else:
                return ("I understand you have a general question. For the most accurate help, "
                       "please specify if you need:\n"
                       "1. Store hours\n"
                       "2. Contact information\n"
                       "3. Or let us know what other information you need")