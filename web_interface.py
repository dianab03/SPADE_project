from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from typing import Optional
import asyncio
import uuid
from blackboard import Blackboard
from CreateAgent import CustomerAgent, RefundAgent, ProductIssueAgent, GeneralRequestAgent

app = FastAPI()
templates = Jinja2Templates(directory="templates")

agents = {}
blackboard = None

@app.on_event("startup")
async def startup_event():
    global blackboard, agents
    XMPP_SERVER = "172.19.104.51"
    
    blackboard = Blackboard()
    
    agents["customer"] = CustomerAgent(f"customer@{XMPP_SERVER}", "password", blackboard, [])
    agents["refund"] = RefundAgent(f"refund_agent@{XMPP_SERVER}", "password", blackboard)
    agents["product_issue"] = ProductIssueAgent(f"product_issue_agent@{XMPP_SERVER}", "password", blackboard)
    agents["general"] = GeneralRequestAgent(f"general_request_agent@{XMPP_SERVER}", "password", blackboard)
    
    for agent in agents.values():
        await agent.start(auto_register=True)

@app.on_event("shutdown")
async def shutdown_event():
    for agent in agents.values():
        await agent.stop()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/submit")
async def submit_query(
    request: Request,
    query_type: str = Form(...),
    query_text: str = Form(...)
):
    task_id = str(uuid.uuid4())
    task_data = {"type": query_type, "data": query_text, "status": "new"}
    
    await blackboard.add_task(task_id, task_data)
    
    for _ in range(10):  
        await asyncio.sleep(1)
        task = await blackboard.get_task(task_id)
        if task and task.get("status") == "completed":
            return templates.TemplateResponse(
                "result.html",
                {
                    "request": request,
                    "result": task.get("result", "No response received"),
                    "query_type": query_type,
                    "query_text": query_text
                }
            )
    
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "result": "Request timed out. Please try again.",
            "query_type": query_type,
            "query_text": query_text
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) 