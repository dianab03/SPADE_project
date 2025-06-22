import asyncio
import time
import uuid

from spade.agent import Agent
from AgentBehaviors import *

class CustomerAgent(Agent):
    def __init__(self, jid, password, blackboard, queries):
        super().__init__(jid, password)
        self.blackboard = blackboard
        self.queries = queries

    async def setup(self):
        print(f"CustomerAgent {self.jid} starting...")
        b = PostTaskAndCheckResultBehaviour(self.blackboard, self.queries)
        self.add_behaviour(b)

class RefundAgent(Agent):
    def __init__(self, jid, password, blackboard):
        super().__init__(jid, password)
        self.blackboard = blackboard
        
    async def setup(self):
        print(f"RefundAgent {self.jid} starting...")
        b = ProcessTaskBehaviour(self.blackboard, "refund")
        self.add_behaviour(b)

class ProductIssueAgent(Agent):
    def __init__(self, jid, password, blackboard):
        super().__init__(jid, password)
        self.blackboard = blackboard

    async def setup(self):
        print(f"ProductIssueAgent {self.jid} starting...")
        b = ProcessTaskBehaviour(self.blackboard, "product_issue")
        self.add_behaviour(b)

class GeneralRequestAgent(Agent):
    def __init__(self, jid, password, blackboard):
        super().__init__(jid, password)
        self.blackboard = blackboard

    async def setup(self):
        print(f"GeneralRequestAgent {self.jid} starting...")
        b = ProcessTaskBehaviour(self.blackboard, "general_request")
        self.add_behaviour(b)