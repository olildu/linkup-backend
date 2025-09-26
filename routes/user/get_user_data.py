import time
from fastapi import APIRouter, Body, Depends, HTTPException, status
import jwt
import psycopg2
from jwt import PyJWTError

from controllers.db_controller import conn
from models.preference_model import PreferenceModel
from models.update_request_model import UpdateRequestModel
from constants.global_constants import ALGORITHM, SECRET_KEY, oauth2_scheme
from utilities.token.token_utilities import decode_token
from utilities.user.user_utilities import get_user_details
from psycopg2.extras import Json

user_router = APIRouter(prefix="/user")

@user_router.get("/get/detail/{user_id}")
async def get_user_data(user_id: int, token: str = Depends(oauth2_scheme)):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"} 
        )

    cursor = None

    try:
       return get_user_details(user_id)
    except psycopg2.Error as e:
        print(f"Database error during user retrieval: {e}")
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving user data"
        )
    finally:
        if cursor:
            cursor.close()

@user_router.get("/get/preferences")
async def get_user_preferences(token: str = Depends(oauth2_scheme)):
    user_id = decode_token(token)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT key, value FROM user_preferences WHERE user_id = %s", (user_id,))
        preferences = cursor.fetchall()

        if not preferences:
            return {"message": "No preferences found for this user"}

        preference_dict = {key: value for key, value in preferences}
        user_preferences = PreferenceModel(**preference_dict)

        return user_preferences

    except psycopg2.Error as e:
        print(f"Database error during preference retrieval: {e}")
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving user preferences"
        )
    finally:
        cursor.close()

@user_router.post("/update/metadata")
async def update_user_metadata(
    update_pfp: bool = False,                      
    body: UpdateRequestModel = Body(...),          
    token: str = Depends(oauth2_scheme)            
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: user id missing")
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    update_data = body.model_dump(exclude_none=True)
    cursor = None

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    try:
        cursor = conn.cursor()

        # Handle 'profile_picture' separately
        if 'profile_picture' in update_data and update_pfp:
            profile_picture = update_data.get("profile_picture")
            if profile_picture and not isinstance(profile_picture, dict):
                raise HTTPException(status_code=400, detail="Invalid input: profile_picture")
            cursor.execute(
                "UPDATE users SET profile_picture = %s WHERE id = %s",
                (Json(profile_picture), user_id)
            )
            conn.commit()
            return {"message": "User metadata updated successfully"}

        # Update or insert other metadata
        for key, value in update_data.items():
            cursor.execute("SELECT 1 FROM user_metadata WHERE user_id = %s AND key = %s", (user_id, key))
            exists = cursor.fetchone()
            if exists:
                query = "UPDATE user_metadata SET value = %s WHERE user_id = %s AND key = %s"
                cursor.execute(
                    query,
                    (str(value), user_id, key)
                )
            else:
                cursor.execute(
                    "INSERT INTO user_metadata (user_id, key, value) VALUES (%s, %s, %s)",
                    (user_id, key, str(value))
                )

        conn.commit()

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database update failed")
    finally:
        if cursor:
            cursor.close()

    return {"message": "User metadata updated successfully"}

@user_router.post('/update/preferences')
async def update_user_preferences(body: PreferenceModel, token: str = Depends(oauth2_scheme)):

    id = decode_token(token)
    cursor = conn.cursor()

    try:
        for key, value in body.model_dump().items():
            # Delete if value is None (null)
            if value is None or value == "Don't mind":
                cursor.execute('''
                    DELETE FROM user_preferences
                    WHERE user_id = %s AND key = %s;
                ''', (id, key))
            else:
                cursor.execute('''
                    INSERT INTO user_preferences (user_id, key, value)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id, key) DO UPDATE
                    SET value = EXCLUDED.value;
                ''', (id, key, value))
            
        conn.commit()

        return {"message": "Preferences updated successfully"}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
