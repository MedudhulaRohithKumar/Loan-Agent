class ValidationAgent:
    """Agent responsible for scrutinizing the data and documents."""
    
    async def validate(self, intake_data: dict):
        remarks = []
        is_valid = True
        
        financials = intake_data.get("financials", {})
        
        if financials.get("annual_income", 0) <= 0:
            is_valid = False
            remarks.append("Annual income must be a valid positive amount.")
            
        if financials.get("loan_amount", 0) <= 0:
            is_valid = False
            remarks.append("Requested loan amount must be positive.")
            
        if financials.get("loan_term") not in [12, 36, 60]:
            is_valid = False
            remarks.append("Invalid loan term selected.")
            
        if financials.get("employment_status") not in [0, 1, 2]:
            is_valid = False
            remarks.append("Invalid employment status.")
            
        return {
            "is_valid": is_valid,
            "remarks": " | ".join(remarks) if remarks else "All data and documents validated successfully."
        }
