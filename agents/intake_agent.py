class IntakeAgent:
    """Agent responsible for ingesting and structuring raw loan application data."""
    
    async def process(self, **kwargs):
        # In a real system, this agent might use an LLM or OCR to extract data from unstructured text.
        # Here we just gracefully structure the incoming data to be used by subsequent agents.
        structured_data = {
            "applicant": {
                "first_name": kwargs.get("first_name"),
                "last_name": kwargs.get("last_name"),
                "email": kwargs.get("email"),
            },
            "financials": {
                "annual_income": float(kwargs.get("annual_income", 0)),
                "loan_amount": float(kwargs.get("loan_amount", 0)),
                "credit_score": int(kwargs.get("credit_score", 0)),
                "employment_status": int(kwargs.get("employment_status", 0)),
                "housing_status": int(kwargs.get("housing_status", 0)),
                "loan_term": int(kwargs.get("loan_term", 36))
            }
        }
        return structured_data
