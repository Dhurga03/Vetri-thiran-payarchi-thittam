from fastapi import APIRouter, Depends, HTTPException, Response

from ..database import get_connection
from ..dependencies import get_current_user
from ..schemas import LoginRequest, RegisterRequest
from ..security import (
    create_access_token,
    hash_password,
    verify_password
)


router = APIRouter(
    tags=["Authentication"]
)


@router.post("/register")
def register(
    data: RegisterRequest,
    response: Response
):

    connection = get_connection()

    existing_user = connection.execute(
        """
        SELECT id
        FROM users
        WHERE email = ?
        """,
        (data.email.lower(),)
    ).fetchone()


    if existing_user:

        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )


    password_hash = hash_password(
        data.password
    )


    cursor = connection.execute(
        """
        INSERT INTO users
        (
            name,
            email,
            password_hash
        )
        VALUES (?, ?, ?)
        """,
        (
            data.name.strip(),
            data.email.lower(),
            password_hash
        )
    )


    connection.commit()

    user_id = cursor.lastrowid

    connection.close()


    token = create_access_token(
        user_id
    )


    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=86400
    )


    return {
        "message": "Registration successful.",
        "user_id": user_id
    }


@router.post("/login")
def login(
    data: LoginRequest,
    response: Response
):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (data.email.lower(),)
    ).fetchone()

    connection.close()


    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )


    if not verify_password(
        data.password,
        user["password_hash"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )


    token = create_access_token(
        user["id"]
    )


    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=86400
    )


    return {
        "message": "Login successful.",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }


@router.post("/logout")
def logout(response: Response):

    response.delete_cookie(
        "access_token"
    )

    return {
        "message": "Logged out successfully."
    }


@router.get("/session-info")
def session_info(
    user=Depends(get_current_user)
):

    return {
        "logged_in": True,
        "user": user
    }


@router.get("/session-data")
def session_data(
    user=Depends(get_current_user)
):

    connection = get_connection()

    count = connection.execute(
        """
        SELECT COUNT(*)
        FROM recommendations
        WHERE user_id = ?
        """,
        (user["id"],)
    ).fetchone()[0]

    connection.close()


    return {
        "user": user,
        "recommendation_count": count
    }