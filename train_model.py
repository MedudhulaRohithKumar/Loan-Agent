import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib

print("Loading data...")
df = pd.read_csv('loan_data.csv')

X = df[['annual_income', 'loan_amount', 'credit_score', 'employment_status', 'housing_status', 'loan_term']]
y = df['approved']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training Ensemble Model (Random Forest, Gradient Boosting, Logistic Regression)...")

# Create individual models
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)

# Logistic Regression works better with scaled features
lr_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('lr', LogisticRegression(random_state=42))
])

# Create an ensemble of the three models using "soft" voting (averaging probabilities)
ensemble_model = VotingClassifier(
    estimators=[
        ('rf', rf_model), 
        ('gb', gb_model), 
        ('lr', lr_pipeline)
    ],
    voting='soft'
)

# Fit the ensemble
ensemble_model.fit(X_train, y_train)

# Evaluate
y_pred = ensemble_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Ensemble Model Accuracy: {accuracy * 100:.2f}%")

joblib.dump(ensemble_model, 'loan_model.joblib')
print("Model saved to loan_model.joblib successfully!")
