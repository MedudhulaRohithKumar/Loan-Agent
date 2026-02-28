import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Generate 1000 dummy samples
n_samples = 1000

# Features
incomes = np.random.normal(loc=80000, scale=30000, size=n_samples).clip(min=15000)
loan_amounts = np.random.normal(loc=150000, scale=80000, size=n_samples).clip(min=5000)
credit_scores = np.random.normal(loc=680, scale=60, size=n_samples).clip(min=300, max=850).astype(int)

# Documents: REMOVED

# New Features
# Employment Status: 0=Unemployed, 1=Self-Employed, 2=Employed
employment_status = np.random.choice([0, 1, 2], size=n_samples, p=[0.1, 0.2, 0.7])

# Housing Status: 0=Rent, 1=Mortgage, 2=Own
housing_status = np.random.choice([0, 1, 2], size=n_samples, p=[0.4, 0.4, 0.2])

# Loan Term (Months): 12, 36, 60
loan_term = np.random.choice([12, 36, 60], size=n_samples, p=[0.2, 0.5, 0.3])

# Logic for Approval (Simulating Bank Policy)
dti = loan_amounts / incomes
approved = np.zeros(n_samples, dtype=int)

for i in range(n_samples):
    chance = 0.5
    
    # Credit score impact
    if credit_scores[i] < 600:
        chance -= 0.6
    elif credit_scores[i] > 720:
        chance += 0.3
        
    # DTI impact
    if dti[i] > 0.5:
        chance -= 0.4
    elif dti[i] < 0.3:
        chance += 0.2
        
    # Employment impact
    if employment_status[i] == 0: # Unemployed
        chance -= 0.5
    elif employment_status[i] == 2: # Employed
        chance += 0.2
        
    # Housing impact
    if housing_status[i] == 2: # Own outright
        chance += 0.15
    elif housing_status[i] == 0: # Rent
        chance -= 0.1
        
    # Term impact (longer term = slightly higher risk)
    if loan_term[i] == 60:
        chance -= 0.1
        
    # Random noise
    chance += np.random.normal(0, 0.1)
    
    approved[i] = 1 if chance > 0.5 else 0

# Create dataframe
df = pd.DataFrame({
    'annual_income': incomes.round(2),
    'loan_amount': loan_amounts.round(2),
    'credit_score': credit_scores,
    'employment_status': employment_status,
    'housing_status': housing_status,
    'loan_term': loan_term,
    'approved': approved
})

# Save to CSV
df.to_csv('loan_data.csv', index=False)
print("loan_data.csv generated with", n_samples, "samples.")
