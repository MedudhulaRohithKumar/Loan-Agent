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
                "credit_score": int(kwargs.get("credit_score", 0))
            },
            "documents": {
                "identity_doc": kwargs.get("identity_doc_name"),
                "income_proof": kwargs.get("income_doc_name")
            }
        }
        return structured_data
