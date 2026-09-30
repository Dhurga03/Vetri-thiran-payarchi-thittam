import json

from fastapi import APIRouter, Depends

from ..database import get_connection
from ..dependencies import get_current_user


router = APIRouter(
    tags=["History"]
)


@router.get("/history")
def get_history(
    user=Depends(get_current_user)
):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            planner,
            request_json,
            response_json,
            created_at
        FROM recommendations
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 50
        """,
        (user["id"],)
    ).fetchall()


    connection.close()


    result = []


    for row in rows:

        result.append(
            {
                "id": row["id"],
                "planner": row["planner"],
                "request": json.loads(
                    row["request_json"]
                ),
                "response": json.loads(
                    row["response_json"]
                ),
                "created_at": row["created_at"]
            }
        )


    return result