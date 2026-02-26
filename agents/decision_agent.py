import joblib
import os
import pandas as pd

class DecisionAgent:
    """Agent responsible for making the final approval or rejection decision using Machine Learning."""
    
    def __init__(self):
        self.model = None
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "..", "loan_model.joblib")
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            
    async def decide(self, intake_data: dict, validation_result: dict):
        financials = intake_data.get("financials", {})
        documents = intake_data.get("documents", {})
        
        annual_income = financials.get("annual_income", 1)
        loan_amount = financials.get("loan_amount", 0)
        credit_score = financials.get("credit_score", 0)
        
        # Document flags
        has_id = 1 if documents.get("identity_doc") else 0
        has_income = 1 if documents.get("income_proof") else 0
        
        remarks = []
        status = "Success"
        
        if not self.model:
            # Fallback logic if model is missing
            status = "Rejected"
            remarks.append("System Error: ML Decision model is currently unavailable.")
        else:
            # Prepare feature DataFrame (to avoid scikit-learn warnings about feature names)
            features = pd.DataFrame([{
                'annual_income': annual_income,
                'loan_amount': loan_amount,
                'credit_score': credit_score,
                'has_identity_doc': has_id,
                'has_income_proof': has_income
            }])
            
            # Predict using Random Forest
            prediction = self.model.predict(features)[0]
            probability = self.model.predict_proba(features)[0][1] # Probability of Approval (class 1)
            
            prob_percent = probability * 100
            
            if prediction == 1:
                status = "Success"
                remarks.append(f"AI Model approved application with {prob_percent:.1f}% confidence.")
                if has_id and has_income:
                    remarks.append("Full documentation provided significantly boosted approval chances.")
                elif not has_id or not has_income:
                    remarks.append("Approved despite missing optimal documents due to strong financials.")
            else:
                status = "Rejected"
                remarks.append(f"AI Model rejected application (Confidence: {100 - prob_percent:.1f}%).")
                if not has_id or not has_income:
                    remarks.append("Missing documents greatly reduced your chances of approval.")
                if credit_score < 650:
                    remarks.append("Credit score is deemed too risky by the algorithm.")

        if status == "Rejected":
            final_remarks = "Loan request failed. " + " ".join(remarks)
        else:
            final_remarks = "Loan origination approved! " + " ".join(remarks)
            
        return {
            "status": status,
            "remarks": final_remarks
        }
