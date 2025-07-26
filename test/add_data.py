import random
import json
import requests
from faker import Faker
from datetime import date

fake = Faker()

genders = ["Male", "Female"]
religions = ["Islam", "Sikhism", "Jainism", "Christianity", "Hinduism", "Buddhism", "Others"]
smoking_options = ["Yes", "Trying to quit", "Occasionally", "No", "No, prefer non-smokers"]
drinking_options = ["Yes", "Trying to quit", "Occasionally", "No", "No, prefer non-drinkers"]
looking_for_options = ["Casual", "Open to anything", "Serious", "Friends", "Not sure yet"]
staying_options = ["Campus Hostel", "PG", "Home", "Flat", "Other"]
majors = ["Computer Science", "Mechanical Engineering", "Design", "Physics", "Psychology", "Law", "Economics"]

def random_dob():
    return fake.date_of_birth(minimum_age=18, maximum_age=25).isoformat()

def generate_user():
    gender = random.choice(genders)
    return {
        "email": fake.email(),
        "password": fake.password(special_chars=True, digits=True, upper_case=True, lower_case=True),
        "username": fake.user_name(),
        "dob": random_dob(),
        "gender": gender,
        "interested_gender": random.choice([g for g in genders if g != gender]),
        "university_major": random.choice(majors),
        "university_year": random.randint(1, 4),
        "university_id": 1,
        "photos": [f"https://picsum.photos/200/{random.randint(300, 350)}" for _ in range(random.randint(2, 4))],
        "profile_picture": f"https://picsum.photos/seed/{fake.uuid4()}/200/200",
        "about": fake.sentence(),
        "currently_staying": random.choice(staying_options),
        "hometown": fake.city(),
        "height": random.randint(150, 190),
        "weight": random.randint(45, 85),
        "religion": random.choice(religions),
        "smoking_info": random.choice(smoking_options),
        "drinking_info": random.choice(drinking_options),
        "looking_for": random.choice(looking_for_options)
    }

users = [generate_user() for _ in range(40)]

for i, user in enumerate(users, 1):
    response = requests.post("http://127.0.0.1:8000/register", json=user)
    print(f"[{i}] Status: {response.status_code} | Response: {response.text}")
