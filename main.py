from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from agents.intake_agent import IntakeAgent
from agents.validation_agent import ValidationAgent
from agents.decision_agent import DecisionAgent

app = FastAPI(title="Autonomous Loan Origination Agentic System")

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

# Mount the static directory
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

intake_agent = IntakeAgent()
validation_agent = ValidationAgent()
decision_agent = DecisionAgent()

from fastapi.responses import FileResponse

import uuid
import datetime

applications = []

def generate_app_id():
    return f"APP-{datetime.datetime.now().strftime('%y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

def format_currency(val):
    return f"${val:,.0f}"

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.get("/dashboard")
async def get_dashboard():
    return FileResponse("static/dashboard.html")

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    approved = sum(1 for a in applications if a["decision"] == "APPROVED")
    denied = sum(1 for a in applications if a["decision"] == "REJECTED")
    review = sum(1 for a in applications if a["decision"] == "REVIEW")
    
    return {
        "stats": {
            "approved": approved,
            "denied": denied,
            "review": review,
            "queue": 0,
            "total_processed": len(applications)
        },
        "applications": applications
    }

@app.post("/api/apply")
async def apply_loan(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    annual_income: float = Form(...),
    loan_amount: float = Form(...),
    credit_score: int = Form(...),
    identity_document: UploadFile = File(None),
    income_proof: UploadFile = File(None)
):
    try:
        # Phase 1: Intake
        intake_data = await intake_agent.process(
            first_name=first_name,
            last_name=last_name,
            email=email,
            annual_income=annual_income,
            loan_amount=loan_amount,
            credit_score=credit_score,
            identity_doc_name=identity_document.filename if identity_document else None,
            income_doc_name=income_proof.filename if income_proof else None
        )
        
        # Phase 2: Validation
        validation_result = await validation_agent.validate(intake_data)
        if not validation_result.get("is_valid"):
            decision_label = "REJECTED"
            remarks = validation_result.get("remarks")
            status_code = 400
            stage = "Validation Agent"
        else:
            # Phase 3: Decision
            decision_result = await decision_agent.decide(intake_data, validation_result)
            decision_label = decision_result.get("status").upper()
            if decision_label == "SUCCESS":
                decision_label = "APPROVED"
            remarks = decision_result.get("remarks")
            status_code = 200
            stage = "Decision Agent"

        # Save to memory
        app_id = generate_app_id()
        rate = "6.875% APR" if decision_label == "APPROVED" else "N/A"
        initials = f"{first_name[0]}{last_name[0]}".upper()
        
        safe_income = float(annual_income) if float(annual_income) > 0 else 1.0
        dti_val = (float(loan_amount) / safe_income) * 100
        
        new_app = {
            "initials": initials,
            "name": f"{first_name} {last_name}",
            "id": app_id,
            "amt": format_currency(float(loan_amount)),
            "type": "PERSONAL",
            "dti": f"{dti_val:.1f}%",
            "score": int(credit_score),
            "decision": decision_label,
            "rate": rate,
            "desc": f"Personal loan · {format_currency(float(loan_amount))} · {first_name} {last_name}",
            "label": app_id,
            "created_at": datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S UTC")
        }
        applications.insert(0, new_app)
        
        return JSONResponse(status_code=status_code, content={
            "status": decision_label.capitalize() if decision_label != "APPROVED" else "Success",
            "remarks": remarks,
            "stage": stage
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
