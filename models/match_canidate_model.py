import ast
import re
from typing import Literal, Optional
from matplotlib.dates import relativedelta
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from datetime import date, datetime

class MatchCandidateModel(BaseModel):
    #Core
    id: int
    username: str
    gender: Literal["Male", "Female"]
    university_id: int
    profile_picture: str
    
    #Metadata
    dob: date

    university_major: str
    university_year: int
 
    photos: list[str]
    about: str

    currently_staying: Literal["Campus Hostel", "PG", "Home", "Flat", "Other"]
    hometown: str

    #Interests
    height: Optional[int] = None
    weight: Optional[int] = None

    religion: Optional[Literal["Islam", "Sikhism", "Jainism", "Christianity", "Hinduism", "Buddhism", "Others"]]

    smoking_info: Optional[Literal["Yes","Trying to quit","Occasionally","No","No, prefer non-smokers"]]
    drinking_info: Optional[Literal["Yes","Trying to quit","Occasionally","No","No, prefer non-drinkers"]]

    looking_for: Optional[Literal["Casual", "Open to anything", "Serious", "Friends", "Not sure yet"]]

    model_config = {
        "extra": "ignore",
    }

def build_candidate_model(user_metadata: dict, core_data: tuple) -> MatchCandidateModel:
    """
    user_metadata: dict mapping metadata key -> value for a single user
    core_data: tuple(username, gender, university_id, profile_picture)
    """

    typed_data = {
        "id" : core_data[0],
        "username": core_data[1],
        "gender": core_data[2],
        "university_id": int(core_data[3]),
        "profile_picture": core_data[4],

        "dob": datetime.strptime(user_metadata["dob"], "%Y-%m-%d").date(),

        "university_major": user_metadata["university_major"],
        "university_year": int(user_metadata["university_year"]),

        "photos": ast.literal_eval(user_metadata["photos"]),
        "about": user_metadata["about"],
        "currently_staying": user_metadata["currently_staying"],
        "hometown": user_metadata["hometown"],

        "height": int(user_metadata["height"]) if user_metadata.get("height") else None,
        "weight": int(user_metadata["weight"]) if user_metadata.get("weight") else None,

        "religion": user_metadata["religion"].strip() if user_metadata.get("religion") and user_metadata["religion"].strip() else None,


        "smoking_info": user_metadata["smoking_info"].strip() if user_metadata.get("smoking_info") and user_metadata["smoking_info"].strip() else None,
        "drinking_info": user_metadata["drinking_info"].strip() if user_metadata.get("drinking_info") and user_metadata["drinking_info"].strip() else None,

        "looking_for": user_metadata["looking_for"].strip() if user_metadata.get("looking_for") and user_metadata["looking_for"].strip() else None,
    }

    return MatchCandidateModel(**typed_data)