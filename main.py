from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import datetime

from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models

from agents.intake_agent import IntakeAgent
from agents.validation_agent import ValidationAgent
from agents.decision_agent import DecisionAgent

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Autonomous Loan Origination Agentic System")

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

# Mount the static directory
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

intake_agent = IntakeAgent()
validation_agent = ValidationAgent()
decision_agent = DecisionAgent()

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
async def get_dashboard_data(db: Session = Depends(get_db)):
    db_apps = db.query(models.Application).order_by(models.Application.id.desc()).all()
    
    approved = sum(1 for a in db_apps if a.status == "Approved")
    denied = sum(1 for a in db_apps if a.status == "Rejected")
    error = sum(1 for a in db_apps if a.status == "Error")
    
    # Format for the frontend dashboard
    formatted_apps = []
    for app in db_apps:
        safe_income = float(app.annual_income) if app.annual_income and float(app.annual_income) > 0 else 1.0
        dti_val = (float(app.loan_amount) / safe_income) * 100 if app.loan_amount else 0
        rate = "6.875% APR" if app.status == "Approved" else "N/A"
        initials = f"{app.first_name[0]}{app.last_name[0]}".upper() if app.first_name and app.last_name else "??"
        
        formatted_apps.append({
            "initials": initials,
            "name": f"{app.first_name} {app.last_name}",
            "id": f"APP-{app.id:04d}",
            "amt": format_currency(float(app.loan_amount)) if app.loan_amount else "$0",
            "type": "PERSONAL",
            "dti": f"{dti_val:.1f}%",
            "score": app.credit_score,
            "decision": app.status.upper() if app.status else "UNKNOWN",
            "rate": rate,
            "desc": f"Confidence: {app.confidence:.1f}% · {format_currency(float(app.loan_amount))} · {app.first_name}",
            "label": f"APP-{app.id:04d}",
            "created_at": "Today"
        })
    
    return {
        "stats": {
            "approved": approved,
            "denied": denied,
            "review": error,
            "queue": 0,
            "total_processed": len(db_apps)
        },
        "applications": formatted_apps
    }

@app.post("/api/apply")
async def apply_loan(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    annual_income: float = Form(...),
    loan_amount: float = Form(...),
    credit_score: int = Form(...),
    employment_status: int = Form(...),
    housing_status: int = Form(...),
    loan_term: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # DB Record Init
        new_app = models.Application(
            first_name=first_name,
            last_name=last_name,
            email=email,
            annual_income=annual_income,
            loan_amount=loan_amount,
            credit_score=credit_score,
            employment_status=employment_status,
            housing_status=housing_status,
            loan_term=loan_term,
            status="Processing",
            confidence=0.0,
            remarks=""
        )
        db.add(new_app)
        db.commit()
        db.refresh(new_app)

        # Phase 1: Intake
        intake_data = await intake_agent.process(
            first_name=first_name,
            last_name=last_name,
            email=email,
            annual_income=annual_income,
            loan_amount=loan_amount,
            credit_score=credit_score,
            employment_status=employment_status,
            housing_status=housing_status,
            loan_term=loan_term
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
            
            # Extract confidence for DB
            import re
            match = re.search(r'(\d+\.\d+)%', remarks)
            if match:
                confidence_score = float(match.group(1))
            else:
                confidence_score = 0.0

        # Save to DB
        new_app = models.Application(
            first_name=first_name,
            last_name=last_name,
            email=email,
            annual_income=annual_income,
            loan_amount=loan_amount,
            credit_score=credit_score,
            employment_status=employment_status,
            housing_status=housing_status,
            loan_term=loan_term,
            status=decision_label.capitalize() if decision_label != "APPROVED" else "Approved",
            confidence=confidence_score if 'confidence_score' in locals() else 0.0,
            remarks=remarks
        )
        db.add(new_app)
        db.commit()
        
        return JSONResponse(status_code=status_code, content={
            "status": decision_label.capitalize() if decision_label != "APPROVED" else "Success",
            "remarks": remarks,
            "stage": stage,
            "metrics": decision_result.get("metrics", {})
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
