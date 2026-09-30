import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile
)

from ..database import get_connection
from ..dependencies import get_current_user
from ..schemas import (
    HomeRequest,
    PartyRequest
)

from ..services.gemini_service import (
    generate_recommendation
)


router = APIRouter(
    tags=["Planners"]
)


def save_history(
    user_id: int,
    planner: str,
    request_data: dict,
    response_data: dict
):
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO recommendations
            (
                user_id,
                planner,
                request_json,
                response_json
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                planner,
                json.dumps(
                    request_data,
                    ensure_ascii=False
                ),
                json.dumps(
                    response_data,
                    ensure_ascii=False
                )
            )
        )

        connection.commit()

    finally:
        connection.close()


@router.post("/generate-home")
async def generate_home(
    data: HomeRequest,
    user=Depends(get_current_user)
):
    request_data = data.model_dump()

    # generate_recommendation() is synchronous,
    # so do NOT use await here.
    result = generate_recommendation(
        planner="home",
        data=request_data
    )

    save_history(
        user["id"],
        "home",
        request_data,
        result
    )

    return result


@router.post("/generate-party")
async def generate_party(
    data: PartyRequest,
    user=Depends(get_current_user)
):
    request_data = data.model_dump()

    # generate_recommendation() is synchronous,
    # so do NOT use await here.
    result = generate_recommendation(
        planner="party",
        data=request_data
    )

    save_history(
        user["id"],
        "party",
        request_data,
        result
    )

    return result


@router.post("/generate-jewelry")
async def generate_jewelry(
    budget: float = Form(...),
    occasion: str = Form(...),
    style: str = Form("Elegant"),
    outfit_color: str = Form(""),
    notes: str = Form(""),
    outfit_image: UploadFile | None = File(None),
    user=Depends(get_current_user)
):
    image_bytes = None
    image_mime = None

    if outfit_image:
        image_bytes = await outfit_image.read()
        image_mime = outfit_image.content_type

    request_data = {
        "budget": budget,
        "occasion": occasion,
        "style": style,
        "outfit_color": outfit_color,
        "notes": notes
    }

    # generate_recommendation() is synchronous,
    # so do NOT use await here.
    result = generate_recommendation(
        planner="jewelry",
        data=request_data,
        image_bytes=image_bytes,
        image_mime=image_mime
    )

    save_history(
        user["id"],
        "jewelry",
        request_data,
        result
    )

    return result


@router.get("/recommendations-details")
async def recommendation_details(
    planner: str,
    user=Depends(get_current_user)
):
    return {
        "message": (
            "Create a recommendation from the "
            "corresponding planner."
        ),
        "planner": planner
    }