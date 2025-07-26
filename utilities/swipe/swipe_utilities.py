from controllers.logger_controller import logger_controller


def exists_in_queue(liker_id, liked_id, cursor):
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM user_discovery_pool
            WHERE user_id = %s
            AND %s = ANY(match_queue)
        ) AS exists_in_queue;
    """,  (liker_id, liked_id))

    result = cursor.fetchone()

    logger_controller.info(f"User {liker_id} exists in match queue for user {liked_id}")

    return result[0]

def handle_post_action(user_id: int, val: int, conn):
    """
    Remove `val` from match_queue array, and add `val` to already_interacted array
    for the user identified by user_id.
    """
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE user_discovery_pool
            SET 
                match_queue = array_remove(match_queue, %s),
                already_interacted = array_append(COALESCE(already_interacted, '{}'), %s)
            WHERE user_id = %s
            RETURNING match_queue, already_interacted;
        """, (val, val, user_id))

        updated = cursor.fetchone()
        conn.commit()
        cursor.close()

        return updated

    except Exception as e:
        conn.rollback()
        cursor.close()
        logger_controller.error(f"Error handling post action for user {user_id}: {e}")
        raise e

def update_discovery_and_post_action(liker_id: int, liked_id: int, conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE user_discovery_pool
            SET match_queue = array_remove(match_queue, %s)
            WHERE user_id = %s;
        """, (liked_id, liker_id))
        conn.commit()
    handle_post_action(liker_id, liked_id, conn)