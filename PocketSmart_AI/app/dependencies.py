from fastapi import Depends, HTTPException, Request

from .database import get_connection
from .security import decode_token


def get_current_user(
    request: Request
):

    token = request.cookies.get(
        "access_token"
    )

    if not token:

        authorization = request.headers.get(
            "Authorization",
            ""
        )

        if authorization.startswith("Bearer "):

            token = authorization[7:]


    if not token:

        raise HTTPException(
            status_code=401,
            detail="Please login first."
        )


    payload = decode_token(token)


    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session."
        )


    user_id = int(
        payload["sub"]
    )


    connection = get_connection()

    user = connection.execute(
        """
        SELECT id, name, email
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    connection.close()


    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found."
        )


    return dict(user)