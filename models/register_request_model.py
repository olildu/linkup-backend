import re
from typing import Literal, Optional
from matplotlib.dates import relativedelta
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from datetime import date

from models.user_model import UserModel

class RegisterRequest(BaseModel):
    #Core
    email: EmailStr
    password: str
    username: str
    
    university_id: int
    profile_picture: str

    gender: Literal["Male", "Female"]

    #Metadata
    dob: date
    interested_gender: Literal["Male", "Female"]

    university_major: str
    university_year: int

    photos: list[str]
    about: str

    currently_staying: Literal["Campus Hostel", "PG", "Home", "Flat", "Other"]
    hometown: str

    #Interests
    height: Optional[int] = None
    weight: Optional[int] = None

    religion: Optional[Literal["Islam", "Sikhism", "Jainism", "Christianity", "Hinduism", "Buddhism", "Others"]] = None

    smoking_info: Optional[Literal["Yes", "Trying to quit", "Occasionally", "No", "No, prefer non-smokers"]] = None
    smoking_status: Optional[bool] = None

    drinking_info: Optional[Literal["Yes", "Trying to quit", "Occasionally", "No", "No, prefer non-drinkers"]] = None
    drinking_status: Optional[bool] = None

    looking_for: Optional[Literal["Casual", "Open to anything", "Serious", "Friends", "Not sure yet"]] = None

    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('dob')
    def check_age(cls, value):
        today = date.today() 
        age = relativedelta(today, value).years
        min_age = 18
        if age < min_age:
            raise ValueError(f'You must be at least {min_age} years old')
        return value

    @field_validator('photos')
    def photos_min_two(cls, v):
        if len(v) < 2:
            raise ValueError('At least two photos are required')
        return v
    
    model_config = {
        "extra": "ignore"
    }



    @model_validator(mode='before')
    def derive_smoking_status(cls, values):
        smoking_info = values.get('smoking_info')
        if smoking_info == "No":
            values['smoking_status'] = False
        else:
            values['smoking_status'] = True
        return values
    
    @model_validator(mode='before')
    def derive_drinking_status(cls, values):
        smoking_info = values.get('drinking_info')
        if smoking_info == "No":
            values['drinking_status'] = False
        else:
            values['drinking_status'] = True
        return values
    
    def to_user_model(self, hashed_password: str) -> UserModel:
        return UserModel(
            hashed_password=hashed_password,
            **self.model_dump()
        )