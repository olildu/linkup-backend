from typing import Optional
from fastapi import HTTPException
import psycopg2
from models.user_model import UserModel
from controllers.db_controller import conn

def add_user_to_db(user: UserModel):
    cursor = None
    user_id = None
    try:
        cursor = conn.cursor()

        # Insert into users table
        insert_user_query = """
            INSERT INTO users (email, password_hash, gender, username, university_id, profile_picture)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        cursor.execute(
            insert_user_query,
            (user.email, user.hashed_password, user.gender, user.username, user.university_id, user.profile_picture),
        )
        user_id = cursor.fetchone()[0]

        # Insert into user_preferences table
        insert_preference_query = """
            INSERT INTO user_preferences (user_id, key, value)
            VALUES (%s, %s, %s)
            RETURNING id;
        """
        cursor.execute(
            insert_preference_query,
            (user_id, "interested_gender", user.interested_gender),
        )

        # Insert into user_metadata table
        insert_metadata_query = """
            INSERT INTO user_metadata (user_id, key, value)
            VALUES (%s, %s, %s);
        """
        metadata = user.model_dump()
        for key, value in metadata.items():
            if key not in ["email", "hashed_password", "gender", "id", "profile_picture", "username", "university_id", "interested_gender"]:
                cursor.execute(insert_metadata_query, (user_id, key, str(value)))

        conn.commit()  
        return user_id

    except psycopg2.Error as e:
        print(f"Database error during user creation: {e}")
        if conn:
            conn.rollback() 
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
 
    finally:
        if cursor:
            cursor.close()

def get_user_from_db(email: Optional[str] = None, id: Optional[int] = None):
    if not email and not id:
        raise HTTPException(status_code=400, detail="Either 'email' or 'id' must be provided.")

    cursor = None
    try:
        cursor = conn.cursor()

        if id is not None and isinstance(id, int):
            select_user_query = """
                SELECT password_hash, email, id
                FROM users
                WHERE id = %s;
            """
            cursor.execute(select_user_query, (id,))
        else:
            select_user_query = """
                SELECT password_hash, email, id
                FROM users
                WHERE email = %s;
            """
            cursor.execute(select_user_query, (email,))
        

        row = cursor.fetchone()
        if not row:
            return None
        
        password_hash, email, id = row
        return {
            "hashed_password": password_hash,
            "email": email,
            "id": id
        }

    except psycopg2.Error as e:
        print(f"Database error during user retrieval: {e}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    finally:
        if cursor:
            cursor.close()