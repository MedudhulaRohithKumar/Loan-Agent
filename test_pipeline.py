import asyncio
from agents.intake_agent import IntakeAgent
from agents.validation_agent import ValidationAgent
from agents.decision_agent import DecisionAgent

async def test():
    intake = IntakeAgent()
    validation = ValidationAgent()
    decision = DecisionAgent()
    
    # Test valid case
    data = await intake.process(
        first_name="Jane", last_name="Doe", email="jane@dt.com",
        annual_income=150000, loan_amount=10000, credit_score=750,
        employment_status=2, housing_status=2, loan_term=12
    )
    
    val = await validation.validate(data)
    assert val['is_valid'] == True
    
    dec = await decision.decide(data, val)
    print("Approval Case:", dec['status'], dec['remarks'])

    # Test reject case
    data2 = await intake.process(
        first_name="John", last_name="Smith", email="john@dt.com",
        annual_income=25000, loan_amount=80000, credit_score=400,
        employment_status=0, housing_status=0, loan_term=60
    )
    val2 = await validation.validate(data2)
    dec2 = await decision.decide(data2, val2)
    print("Reject Case:", dec2['status'], dec2['remarks'])

asyncio.run(test())
print("Pipeline tested successfully.")
