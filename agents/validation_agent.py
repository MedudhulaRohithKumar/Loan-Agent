class ValidationAgent:
    """Agent responsible for scrutinizing the data and documents."""
    
    async def validate(self, intake_data: dict):
        remarks = []
        is_valid = True
        
        financials = intake_data.get("financials", {})
        documents = intake_data.get("documents", {})

        has_identity_doc = 1 if documents.get("identity_doc") else 0
        has_income_proof = 1 if documents.get("income_proof") else 0
            
        if financials.get("annual_income", 0) <= 0:
            is_valid = False
            remarks.append("Annual income must be a valid positive amount.")
            
        if financials.get("loan_amount", 0) <= 0:
            is_valid = False
            remarks.append("Requested loan amount must be positive.")
            
        # Mocking an OCR-type check on actual doc names
        id_doc = documents.get("identity_doc", "")
        if id_doc and "." in id_doc:
            ext = id_doc.rsplit(".", 1)[-1].lower()
            if ext not in ["pdf", "jpg", "jpeg", "png"]:
                is_valid = False
                remarks.append("Identity document format not supported. Use PDF, JPG, or PNG.")

        return {
            "is_valid": is_valid,
            "remarks": " | ".join(remarks) if remarks else "All data and documents validated successfully."
        }
