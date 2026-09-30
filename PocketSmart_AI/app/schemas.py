from typing import Any, Dict, List

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=80
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=128
    )


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


class HomeRequest(BaseModel):

    budget: float = Field(gt=0)

    room_type: str = Field(
        min_length=2,
        max_length=100
    )

    style: str = "Modern"

    items: List[Dict[str, Any]] = []


class PartyRequest(BaseModel):

    budget: float = Field(gt=0)

    guests: int = Field(
        gt=0,
        le=10000
    )

    event_type: str = Field(
        min_length=2,
        max_length=100
    )

    venue: str = ""

    preferences: str = ""


class JewelryRequest(BaseModel):

    budget: float = Field(gt=0)

    occasion: str

    style: str = "Elegant"

    outfit_color: str = ""

    notes: str = ""