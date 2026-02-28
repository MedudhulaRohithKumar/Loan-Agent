import requests
import random
import time
from faker import Faker

fake = Faker()
API_URL = "http://127.0.0.1:8000/api/apply"

def generate_and_submit(count=118):
    print(f"Starting submission of {count} dummy applications...")
    
    success_count = 0
    fail_count = 0
    
    for i in range(count):
        # Generate realistic data
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        
        # Mix of good, bad, and borderline profiles
        profile_type = random.choices(['excellent', 'good', 'risky', 'poor'], weights=[20, 40, 30, 10])[0]
        
        if profile_type == 'excellent':
            annual_income = random.randint(80000, 250000)
            loan_amount = random.randint(5000, 30000)
            credit_score = random.randint(720, 850)
            employment_status = 2  # Employed
            housing_status = 2     # Own
        elif profile_type == 'good':
            annual_income = random.randint(50000, 100000)
            loan_amount = random.randint(5000, 20000)
            credit_score = random.randint(650, 750)
            employment_status = random.choice([1, 2]) # Self-emp or Employed
            housing_status = random.choice([1, 2])    # Rent or Own
        elif profile_type == 'risky':
            annual_income = random.randint(30000, 60000)
            loan_amount = random.randint(15000, 40000) # High DTI
            credit_score = random.randint(580, 680)
            employment_status = random.choice([0, 1, 2])
            housing_status = random.choice([0, 1])
        else:
            annual_income = random.randint(20000, 40000)
            loan_amount = random.randint(10000, 30000)
            credit_score = random.randint(300, 580)
            employment_status = random.choice([0, 1])
            housing_status = random.choice([0, 1])

        loan_term = random.choice([12, 24, 36, 48, 60])
        
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "annual_income": annual_income,
            "loan_amount": loan_amount,
            "credit_score": credit_score,
            "employment_status": employment_status,
            "housing_status": housing_status,
            "loan_term": loan_term
        }
        
        try:
            response = requests.post(API_URL, data=data)
            if response.status_code in [200, 400]: # 400 is normally validation reject, which is fine
                success_count += 1
                res_data = response.json()
                status = res_data.get('status', 'Unknown')
                print(f"[{i+1}/{count}] {first_name} {last_name} -> {status}")
            else:
                fail_count += 1
                print(f"[{i+1}/{count}] Error {response.status_code}")
        except Exception as e:
            fail_count += 1
            print(f"[{i+1}/{count}] Request failed: {e}")
            
        time.sleep(0.1) # Small delay to not overwhelm the local server completely
        
    print(f"\nCompleted! {success_count} succeeded, {fail_count} failed to submit.")

if __name__ == "__main__":
    generate_and_submit(118)
