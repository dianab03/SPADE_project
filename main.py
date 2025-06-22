import asyncio
import time
import uuid
import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from spade.template import Template

from blackboard import *
from AgentBehaviors import *
from CreateAgent import *

# import logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    XMPP_SERVER = "172.19.104.51"

    blackboard = Blackboard()

    customer_queries = [
        {"type": "refund", "data": "Order #R-98765"},
        {"type": "product_issue", "data": "My new toaster is not working"},
        {"type": "general_request", "data": "What are your weekend hours?"},
        {"type": "refund", "data": "Order #R-11223"}
    ]

    customer_agent = CustomerAgent(f"customer@{XMPP_SERVER}", "password", blackboard, customer_queries)
    await customer_agent.start(auto_register=True)

    refund_agent = RefundAgent(f"refund_agent@{XMPP_SERVER}", "password", blackboard)
    await refund_agent.start(auto_register=True)
    
    product_issue_agent = ProductIssueAgent(f"product_issue_agent@{XMPP_SERVER}", "password", blackboard)
    await product_issue_agent.start(auto_register=True)
    
    general_request_agent = GeneralRequestAgent(f"general_request_agent@{XMPP_SERVER}", "password", blackboard)
    await general_request_agent.start(auto_register=True)

    print("\nAll agents started. System is running. Press CTRL+C to stop.")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping agents...")
        await customer_agent.stop()
        await refund_agent.stop()
        await product_issue_agent.stop()
        await general_request_agent.stop()
        print("All agents stopped.")

if __name__ == "__main__":
    spade.run(main())