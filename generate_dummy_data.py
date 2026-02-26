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

# Documents: 0 or 1
has_identity_doc = np.random.choice([0, 1], size=n_samples, p=[0.2, 0.8])
has_income_proof = np.random.choice([0, 1], size=n_samples, p=[0.3, 0.7])

# Logic for Approval (Simulating Bank Policy)
# 1. Base approval chance depends heavily on credit score and DTI (Debt-to-Income)
dti = loan_amounts / incomes
approved = np.zeros(n_samples, dtype=int)

for i in range(n_samples):
    chance = 0.5
    
    # Credit score impact
    if credit_scores[i] < 600:
        chance -= 0.6
    elif credit_scores[i] > 720:
        chance += 0.3
        
    # DTI impact (lower is better, ideally < 0.4)
    if dti[i] > 0.5:
        chance -= 0.4
    elif dti[i] < 0.3:
        chance += 0.2
        
    # Document impact: Providing documents gives a MASSIVE boost to approval chances
    if has_identity_doc[i] == 1:
        chance += 0.2
    else:
        chance -= 0.3
        
    if has_income_proof[i] == 1:
        chance += 0.2
    else:
        chance -= 0.3
        
    # Random noise
    chance += np.random.normal(0, 0.1)
    
    approved[i] = 1 if chance > 0.5 else 0

# Create dataframe
df = pd.DataFrame({
    'annual_income': incomes.round(2),
    'loan_amount': loan_amounts.round(2),
    'credit_score': credit_scores,
    'has_identity_doc': has_identity_doc,
    'has_income_proof': has_income_proof,
    'approved': approved
})

# Save to CSV
df.to_csv('loan_data.csv', index=False)
print("loan_data.csv generated with", n_samples, "samples.")
