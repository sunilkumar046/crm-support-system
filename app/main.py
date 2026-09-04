from fastapi import FastAPI

from app.routers import auth
from app.routers import ticket
from app.routers import category
from app.routers import ticket_response
from app.routers import notification

from app.routers.attachment import router as attachment_router
from app.routers.sla import router as sla_router
from app.routers.audit_log import router as audit_log_router
from app.routers.dashboard import router as dashboard_router


app = FastAPI()


app.include_router(auth.router)

app.include_router(ticket.router)
app.include_router(category.router)
app.include_router(ticket_response.router)
app.include_router(notification.router)

app.include_router(attachment_router)
app.include_router(sla_router)
app.include_router(audit_log_router)
app.include_router(dashboard_router)


@app.get("/")
def home():
    return {
        "message": "CRM Support System API is running"
    }