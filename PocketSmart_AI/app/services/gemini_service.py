import json
import os
import time
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Always reload values from .env
load_dotenv(override=True)


# ============================================================
# GEMINI SDK
# ============================================================

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


# ============================================================
# CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)


_client = None


# ============================================================
# GEMINI CLIENT
# ============================================================

def get_gemini_client():

    global _client

    if _client is not None:
        return _client

    if genai is None:
        raise RuntimeError(
            "google-genai is not installed. "
            "Run: python -m pip install -U google-genai"
        )

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add GEMINI_API_KEY=... to your .env file."
        )

    _client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    return _client


# ============================================================
# JSON PARSER
# ============================================================

def _extract_json(
    text: str
) -> Dict[str, Any]:

    if not text:
        return {
            "recommendations": []
        }

    text = text.strip()

    # Remove Markdown code fences
    if text.startswith("```"):

        lines = text.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # Remove "json" prefix
    if text.lower().startswith("json"):
        text = text[4:].strip()

    # Direct JSON parsing
    try:

        result = json.loads(text)

        if isinstance(result, dict):
            return result

        return {
            "recommendations": result
        }

    except json.JSONDecodeError:
        pass

    # Try extracting JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        possible_json = text[
            start:end + 1
        ]

        try:

            result = json.loads(
                possible_json
            )

            if isinstance(result, dict):
                return result

        except json.JSONDecodeError:
            pass

    return {
        "raw_response": text,
        "recommendations": []
    }


# ============================================================
# GEMINI GENERATION
# ============================================================

def _generate(
    prompt: str,
    image_bytes: Optional[bytes] = None,
    image_mime: Optional[str] = None
) -> Dict[str, Any]:

    client = get_gemini_client()

    contents = []

    # Add image when provided
    if image_bytes:

        if types is None:
            raise RuntimeError(
                "Gemini types are unavailable."
            )

        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=(
                    image_mime
                    or "image/jpeg"
                )
            )
        )

    contents.append(prompt)

    # ========================================================
    # MODEL FALLBACK
    # ========================================================

    models_to_try = [
        GEMINI_MODEL,
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
    ]

    # Remove duplicates
    models_to_try = list(
        dict.fromkeys(
            models_to_try
        )
    )

    last_error = None

    # ========================================================
    # TRY EACH MODEL
    # ========================================================

    for model in models_to_try:

        for attempt in range(1, 3):

            try:

                print(
                    f"[PocketSmart AI] "
                    f"Gemini model: {model} "
                    f"| attempt: {attempt}"
                )

                response = (
                    client.models.generate_content(
                        model=model,
                        contents=contents,
                    )
                )

                text = getattr(
                    response,
                    "text",
                    None
                )

                if not text:

                    return {
                        "error": (
                            "Gemini returned "
                            "an empty response."
                        ),
                        "recommendations": []
                    }

                result = _extract_json(
                    text
                )

                result.setdefault(
                    "ai_model",
                    model
                )

                return result

            except Exception as exc:

                last_error = str(exc)

                print(
                    f"[PocketSmart AI] "
                    f"Gemini error: {last_error}"
                )

                error_upper = (
                    last_error.upper()
                )

                temporary_error = (
                    "503" in error_upper
                    or
                    "UNAVAILABLE" in error_upper
                    or
                    "HIGH DEMAND" in error_upper
                    or
                    "429" in error_upper
                    or
                    "RESOURCE_EXHAUSTED"
                    in error_upper
                )

                # Temporary Gemini error
                if temporary_error:

                    if attempt == 1:

                        print(
                            "[PocketSmart AI] "
                            "Temporary Gemini "
                            "error. Retrying..."
                        )

                        time.sleep(3)

                        continue

                    print(
                        f"[PocketSmart AI] "
                        f"Model {model} unavailable. "
                        "Trying next model..."
                    )

                    break

                # Non-temporary error
                return {
                    "error": last_error,
                    "recommendations": []
                }

    # ========================================================
    # ALL MODELS FAILED
    # ========================================================

    return {
        "error": (
            "All Gemini models are "
            "temporarily unavailable. "
            "Please try again shortly.\n\n"
            f"Last error: {last_error}"
        ),
        "recommendations": []
    }


# ============================================================
# CURRENCY
# ============================================================

def _format_currency(
    value: float
) -> str:

    return f"₹{value:,.0f}"


# ============================================================
# HOME RECOMMENDATION
# ============================================================

def generate_home_recommendation(
    data: Dict[str, Any]
) -> Dict[str, Any]:

    budget = float(
        data.get(
            "budget",
            0
        )
    )

    rooms = data.get(
        "rooms",
        []
    )

    style = data.get(
        "style",
        "Modern"
    )

    city = data.get(
        "city",
        ""
    )

    additional_requirements = data.get(
        "additional_requirements",
        ""
    )

    prompt = f"""
You are PocketSmart AI,
a practical budget planning assistant
for Indian customers.

Create a useful home interior shopping plan.

USER INFORMATION

Budget:
{_format_currency(budget)}

Rooms:
{json.dumps(
    rooms,
    ensure_ascii=False
)}

Preferred style:
{style}

City:
{city}

Additional requirements:
{additional_requirements}

RULES

1. Stay within the total budget.
2. Use realistic approximate Indian prices.
3. Do not claim live availability.
4. Do not invent exact live prices.
5. Recommend practical products/categories.
6. Give affordable alternatives.
7. Explain why every recommendation fits.
8. Return at least 5 recommendations.
9. Return ONLY valid JSON.

Return exactly this structure:

{{
    "planner": "home",
    "total_budget": {budget},
    "budget_used": 0,
    "remaining_budget": {budget},
    "summary": "short summary",
    "budget_breakdown": [
        {{
            "category": "Lighting",
            "allocated_budget": 0,
            "reason": "reason"
        }}
    ],
    "recommendations": [
        {{
            "category": "Lighting",
            "item": "Example item",
            "quantity": 1,
            "estimated_price": 1000,
            "price_range": "₹800 - ₹1,200",
            "reason": "Why it fits",
            "platform": "Amazon",
            "search_url": "https://www.amazon.in/s?k=lighting"
        }}
    ],
    "tips": [
        "tip 1",
        "tip 2"
    ]
}}
"""

    result = _generate(
        prompt
    )

    result.setdefault(
        "planner",
        "home"
    )

    result.setdefault(
        "total_budget",
        budget
    )

    result.setdefault(
        "budget_used",
        0
    )

    result.setdefault(
        "remaining_budget",
        budget
    )

    result.setdefault(
        "summary",
        ""
    )

    result.setdefault(
        "budget_breakdown",
        []
    )

    result.setdefault(
        "recommendations",
        []
    )

    result.setdefault(
        "tips",
        []
    )

    return result


# ============================================================
# PARTY RECOMMENDATION
# ============================================================

def generate_party_recommendation(
    data: Dict[str, Any]
) -> Dict[str, Any]:

    budget = float(
        data.get(
            "budget",
            0
        )
    )

    guests = int(
        data.get(
            "guests",
            1
        )
    )

    event_type = data.get(
        "event_type",
        "Birthday"
    )

    venue = data.get(
        "venue",
        ""
    )

    city = data.get(
        "city",
        ""
    )

    food_preference = data.get(
        "food_preference",
        "Mixed"
    )

    additional_requirements = data.get(
        "additional_requirements",
        ""
    )

    prompt = f"""
You are PocketSmart AI,
an intelligent party budget planner
for Indian customers.

Create a complete practical party plan.

TOTAL BUDGET:
{_format_currency(budget)}

NUMBER OF GUESTS:
{guests}

EVENT TYPE:
{event_type}

VENUE:
{venue}

CITY:
{city}

FOOD PREFERENCE:
{food_preference}

ADDITIONAL REQUIREMENTS:
{additional_requirements}

RULES

1. Stay within the total budget.
2. Allocate the budget between:
   - Food
   - Decoration
   - Venue
   - Entertainment
3. Calculate approximate per-person food cost.
4. Provide practical alternatives.
5. Use realistic approximate Indian prices.
6. Do not claim live availability.
7. Do not invent exact live prices.
8. Return at least 5 recommendations.
9. Return ONLY valid JSON.

Return exactly:

{{
    "planner": "party",
    "total_budget": {budget},
    "guests": {guests},
    "budget_used": 0,
    "remaining_budget": {budget},
    "summary": "short summary",
    "budget_breakdown": [
        {{
            "category": "Food",
            "allocated_budget": 0,
            "percentage": 0,
            "reason": "reason"
        }}
    ],
    "recommendations": [
        {{
            "category": "Food",
            "item": "Example catering option",
            "estimated_price": 5000,
            "price_range": "₹4,000 - ₹6,000",
            "quantity": "{guests} guests",
            "platform": "Search",
            "search_url": "https://www.google.com/search?q=party+catering",
            "reason": "Why this fits"
        }}
    ],
    "tips": [
        "tip 1",
        "tip 2"
    ]
}}
"""

    result = _generate(
        prompt
    )

    result.setdefault(
        "planner",
        "party"
    )

    result.setdefault(
        "total_budget",
        budget
    )

    result.setdefault(
        "guests",
        guests
    )

    result.setdefault(
        "budget_used",
        0
    )

    result.setdefault(
        "remaining_budget",
        budget
    )

    result.setdefault(
        "summary",
        ""
    )

    result.setdefault(
        "budget_breakdown",
        []
    )

    result.setdefault(
        "recommendations",
        []
    )

    result.setdefault(
        "tips",
        []
    )

    return result


# ============================================================
# JEWELRY RECOMMENDATION
# ============================================================

def generate_jewelry_recommendation(
    data: Dict[str, Any],
    image_bytes: Optional[bytes] = None,
    image_mime_type: Optional[str] = None,
) -> Dict[str, Any]:

    budget = float(
        data.get(
            "budget",
            0
        )
    )

    occasion = data.get(
        "occasion",
        "General"
    )

    style = data.get(
        "style",
        "Elegant"
    )

    outfit_description = data.get(
        "outfit_description",
        data.get(
            "notes",
            ""
        )
    )

    city = data.get(
        "city",
        ""
    )

    prompt = f"""
You are PocketSmart AI,
a jewelry recommendation assistant
for Indian customers.

Create jewelry recommendations.

Budget:
{_format_currency(budget)}

Occasion:
{occasion}

Preferred style:
{style}

Outfit description:
{outfit_description}

City:
{city}

If an outfit image is provided,
analyze only visible clothing characteristics:

- dominant colors
- clothing style
- neckline when clearly visible
- overall aesthetic

Do not identify the person.

RULES

1. Stay within the budget.
2. Recommend suitable jewelry.
3. Explain every recommendation.
4. Consider color coordination.
5. Provide affordable alternatives.
6. Use approximate prices.
7. Do not claim live availability.
8. Return at least 5 recommendations.
9. Return ONLY valid JSON.

Return exactly:

{{
    "planner": "jewelry",
    "total_budget": {budget},
    "occasion": "{occasion}",
    "style": "{style}",
    "summary": "short summary",
    "outfit_analysis": {{
        "colors": [],
        "style": "",
        "neckline": "",
        "matching_notes": ""
    }},
    "recommendations": [
        {{
            "type": "Earrings",
            "name": "Example earrings",
            "estimated_price": 999,
            "price_range": "₹800 - ₹1,200",
            "material": "Artificial jewellery",
            "color": "Gold",
            "platform": "Amazon",
            "search_url": "https://www.amazon.in/s?k=gold+earrings",
            "reason": "Why it matches"
        }}
    ],
    "tips": [
        "tip 1",
        "tip 2"
    ]
}}
"""

    result = _generate(
        prompt,
        image_bytes=image_bytes,
        image_mime=image_mime_type
    )

    result.setdefault(
        "planner",
        "jewelry"
    )

    result.setdefault(
        "total_budget",
        budget
    )

    result.setdefault(
        "occasion",
        occasion
    )

    result.setdefault(
        "style",
        style
    )

    result.setdefault(
        "recommendations",
        []
    )

    result.setdefault(
        "tips",
        []
    )

    return result


# ============================================================
# MAIN RECOMMENDATION FUNCTION
# ============================================================

def generate_recommendation(
    planner: str,
    data: Dict[str, Any],
    image_bytes: Optional[bytes] = None,
    image_mime: Optional[str] = None,
) -> Dict[str, Any]:

    planner = planner.lower().strip()

    if planner == "home":

        return generate_home_recommendation(
            data
        )

    if planner == "party":

        return generate_party_recommendation(
            data
        )

    if planner == "jewelry":

        return generate_jewelry_recommendation(
            data=data,
            image_bytes=image_bytes,
            image_mime_type=image_mime
        )

    return {
        "planner": planner,
        "error": (
            f"Unknown planner: {planner}"
        ),
        "recommendations": []
    }