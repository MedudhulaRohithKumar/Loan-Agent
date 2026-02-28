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
        
        annual_income = financials.get("annual_income", 1)
        loan_amount = financials.get("loan_amount", 0)
        credit_score = financials.get("credit_score", 0)
        employment_status = financials.get("employment_status", 0)
        housing_status = financials.get("housing_status", 0)
        loan_term = financials.get("loan_term", 36)
        
        remarks = []
        status = "Success"
        
        if not self.model:
            # Fallback logic if model is missing
            status = "Rejected"
            remarks.append("System Error: ML Decision model is currently unavailable.")
        else:
            # Prepare feature DataFrame
            features = pd.DataFrame([{
                'annual_income': annual_income,
                'loan_amount': loan_amount,
                'credit_score': credit_score,
                'employment_status': employment_status,
                'housing_status': housing_status,
                'loan_term': loan_term
            }])
            
            # Predict using Ensemble
            prediction = self.model.predict(features)[0]
            probability = self.model.predict_proba(features)[0][1] # Probability of Approval (class 1)
            
            prob_percent = probability * 100
            
            if prediction == 1:
                status = "Success"
                remarks.append(f"AI Ensemble approved application with {prob_percent:.1f}% confidence.")
                
                if employment_status == 2 and housing_status == 2:
                    remarks.append("Stable employment and homeownership strongly contributed to the decision.")
                elif credit_score > 700:
                    remarks.append("Excellent credit history drove a favorable outcome.")
            else:
                status = "Rejected"
                remarks.append(f"AI Ensemble rejected application (Confidence: {100 - prob_percent:.1f}%).")
                
                if employment_status == 0:
                    remarks.append("Lack of current employment flagged as high risk.")
                if credit_score < 650:
                    remarks.append("Credit score is deemed too risky by the algorithm.")
                if (loan_amount / max(annual_income, 1)) > 0.4:
                    remarks.append("Debt-to-Income ratio exceeds acceptable thresholds.")

            # Compute normalized metrics for UI (0.0 to 1.0)
            dti = loan_amount / max(annual_income, 1)
            dti_score = max(0, min(1, 1 - (dti / 0.6))) # >60% DTI is 0 score
            
            credit_score_norm = max(0, min(1, (credit_score - 300) / (850 - 300)))
            
            employment_score = employment_status / 2.0 # 0, 0.5, 1.0
            
            metrics = {
                "dti_score": round(dti_score, 2),
                "credit_score": round(credit_score_norm, 2),
                "employment_score": round(employment_score, 2),
                "confidence": round(prob_percent if prediction == 1 else (100 - prob_percent), 2)
            }

        if status == "Rejected":
            final_remarks = "Loan request failed. " + " ".join(remarks)
        else:
            final_remarks = "Loan origination approved! " + " ".join(remarks)
            
        return {
            "status": status,
            "remarks": final_remarks,
            "metrics": metrics if 'metrics' in locals() else {}
        }
