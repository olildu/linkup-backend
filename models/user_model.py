import ast
import re
from typing import Literal, Optional
from matplotlib.dates import relativedelta
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from datetime import date, datetime

class UserModel(BaseModel):
    id: Optional[int] = None

    email: EmailStr
    hashed_password: str
    username: Optional[str] = None
    gender: Optional[Literal["Male", "Female"]] = None
    university_id: int
    profile_picture: Optional[str] = None

    dob: Optional[date] = None
    interested_gender: Optional[Literal["Male", "Female"]] = None

    university_major: Optional[str] = None
    university_year: Optional[int] = None

    photos: list[str] = []
    about: Optional[str] = None

    currently_staying: Optional[Literal["Campus Hostel", "PG", "Home", "Flat", "Other"]] = None
    hometown: Optional[str] = None

    height: Optional[int] = None
    weight: Optional[int] = None

    religion: Optional[Literal["Islam", "Sikhism", "Jainism", "Christianity", "Hinduism", "Buddhism", "Others"]] = None

    smoking_info: Optional[Literal["Yes", "Trying to quit", "Occasionally", "No", "No, prefer non-smokers"]] = None
    smoking_status: Optional[bool] = None

    drinking_info: Optional[Literal["Yes", "Trying to quit", "Occasionally", "No", "No, prefer non-drinkers"]] = None
    drinking_status: Optional[bool] = None

    looking_for: Optional[Literal["Casual", "Open to anything", "Serious", "Friends", "Not sure yet"]] = None

    model_config = {
        "extra": "ignore",
    }

def build_user_model(user_metadata: list, core_data: list, hashed_password: str, user_preferences: list):
    metadata_dict = {item[2]: item[3] for item in user_metadata}
    user_preferences_dict = {item[2]: item[3] for item in user_preferences}

    def parse_optional_int(value):
        return int(value) if value and str(value).isdigit() else None

    def parse_optional_bool(value):
        return value.lower() == "true" if value else None

    def parse_optional_str(value):
        return value.strip() if value and value.strip() else None

    def parse_date(value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date() if value else None
        except:
            return None

    id = int(core_data[0])
    email = core_data[1]

    username = core_data[2] if len(core_data) > 2 else None
    gender = core_data[3] if len(core_data) > 3 else None
    university_id = int(core_data[4]) if len(core_data) > 4 and str(core_data[4]).isdigit() else -1
    profile_picture = core_data[5] if len(core_data) > 5 else None

    typed_data = {
        "id": id,
        "email": email,
        "hashed_password": hashed_password,
        "username": username,
        "dob": parse_date(metadata_dict.get("dob")),
        "gender": gender,
        "interested_gender": user_preferences_dict.get("interested_gender"),
        "university_major": parse_optional_str(metadata_dict.get("university_major")),
        "university_year": parse_optional_int(metadata_dict.get("university_year")),
        "university_id": university_id,
        "profile_picture": profile_picture,
        "photos": ast.literal_eval(metadata_dict.get("photos", "[]")),
        "about": parse_optional_str(metadata_dict.get("about")),
        "currently_staying": parse_optional_str(metadata_dict.get("currently_staying")),
        "hometown": parse_optional_str(metadata_dict.get("hometown")),
        "height": parse_optional_int(metadata_dict.get("height")),
        "weight": parse_optional_int(metadata_dict.get("weight")),
        "religion": parse_optional_str(metadata_dict.get("religion")),
        "smoking_info": parse_optional_str(metadata_dict.get("smoking_info")),
        "smoking_status": parse_optional_bool(metadata_dict.get("smoking_status")),
        "drinking_info": parse_optional_str(metadata_dict.get("drinking_info")),
        "drinking_status": parse_optional_bool(metadata_dict.get("drinking_status")),
        "looking_for": parse_optional_str(metadata_dict.get("looking_for"))
    }

    return UserModel(**typed_data)
