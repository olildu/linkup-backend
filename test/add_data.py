import random
import string
import requests
from faker import Faker
from datetime import date

fake = Faker()

# Utility to generate strong passwords
def generate_strong_password(length=10):
    while True:
        password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*()_+", k=length))
        if any(c in "!@#$%^&*()_+" for c in password):
            return password

# Fixed media
fixed_profile_picture = {
    "file_key": "/profile_pictures/67/pfp_W4dOSZ860.webp",
    "blurhash": "|dQ+Wpxu*0WB%gofayofV@MwaeMwoft7a}o#WBkCShj[WBWBofayRjj[kBxva}X8fQa$azjYj[j@xaj[WCazS5fkt7ayoLxuj[V[jZRkfkozfkozn%fQaxj@Rkf6t7aykCofj[WBfjkBayoLjZf6ofazWBj@j@ayofayf7"
}

fixed_photos = [
    {
        "file_key": "/media/67/5c9d8d55-99a9-4fd7-9c62-6a476cfb6046.jpg",
        "blurhash": "UGOwP]M|E4n$~q%1E1WBRixG-;WBNhxtNH%1"
    },
    {
        "file_key": "/media/67/a7c49d2b-d92b-4688-9362-3b2036a6f456.jpg",
        "blurhash": "UQG8Xpxu009F?bRjxuj[~q%Mxut7NHxuM{of"
    }
]

def create_and_register_user():
    # Fake user credentials
    email = fake.email()
    username = fake.user_name()
    password = generate_strong_password()

    print(f"\n➡️ Creating user {email}")

    # 1. Signup
    signup_resp = requests.post("http://localhost:8000/signup", json={
        "email_hash": email,
        "password": password
    })
    if signup_resp.status_code != 200:
        print("❌ Signup failed:", signup_resp.text)
        return

    # 2. Trigger OTP (normally user gets email, here it's mocked)
    requests.get(f"http://localhost:8000/verify-email?email={email}")

    # 3. Mock OTP verification
    otp_resp = requests.post("http://localhost:8000/verify-otp", json={
        "email": email,
        "otp": "123456"  # Replace this with real OTP if needed
    })
    if otp_resp.status_code != 200:
        print("❌ OTP verification failed:", otp_resp.text)
        return

    email_hash = otp_resp.json().get("email_hash")
    if not email_hash:
        print("❌ No email_hash received")
        return

    # 4. Register full profile
    headers = {"Authorization": f"Bearer {email_hash}"}
    gender = random.choice(["Male", "Female"])
    register_data = {
        "dob": str(fake.date_of_birth(minimum_age=18, maximum_age=30)),
        "gender": gender,
        "height": random.randint(150, 190),
        "weight": random.randint(50, 80),
        "religion": random.choice(["Christianity", "Islam", "Hinduism"]),
        "smokingInfo": random.choice(["Never", "Occasionally"]),
        "drinkingInfo": random.choice(["Never", "Occasionally"]),
        "lookingFor": random.choice(["Friendship", "Relationship"]),
        "currentlyStaying": fake.city(),
        "hometown": fake.city(),
        "bio": fake.sentence(),
        "profile_picture": fixed_profile_picture,
        "photos": fixed_photos
    }

    register_resp = requests.post("http://localhost:8000/register", headers=headers, json=register_data)
    if register_resp.status_code != 200:
        print("❌ Register failed:", register_resp.text)
        return

    print("✅ Registered user successfully")

    # 5. Login and fetch token
    login_resp = requests.post("http://localhost:8000/token", data={
        "username": email,
        "password": password
    })

    if login_resp.status_code != 200:
        print("❌ Login failed:", login_resp.text)
        return

    token = login_resp.json().get("access_token")
    print(f"🔐 Login successful. Access token: {token[:20]}...")

    # You can now use `Authorization: Bearer <token>` to access secure APIs

# ▶️ Run for N users
for _ in range(5):  # Change to any number of users
    create_and_register_user()
