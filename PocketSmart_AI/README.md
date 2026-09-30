# PocketSmart AI

PocketSmart AI is a Generative AI powered budget and recommendation assistant.

It provides three main planners:

1. Home Interior Planner
2. Party Budget Planner
3. Jewelry Budget Planner

The application uses:

- FastAPI
- Python
- Gemini API
- SQLite
- Jinja2
- HTML
- CSS
- JavaScript
- JWT authentication


# PROJECT STRUCTURE

PocketSmart_AI/

    app/

        __init__.py

        main.py

        config.py

        database.py

        security.py

        schemas.py

        dependencies.py

        routes/

            __init__.py

            auth.py

            pages.py

            planners.py

            history.py

        services/

            __init__.py

            catalog.py

            gemini_service.py

        templates/

            base.html

            index.html

            login.html

            register.html

            dashboard.html

            home.html

            party.html

            jewelry.html

            history.html

        static/

            style.css

            app.js


    tests/

        test_app.py


    .vscode/

        launch.json


    .env

    .env.example

    .gitignore

    requirements.txt

    README.md


# REQUIREMENTS

Python 3.10 or newer is recommended.


# INSTALLATION

Open the project folder in VS Code.


## STEP 1

Create a virtual environment.

Windows:

    py -m venv .venv


## STEP 2

Activate the environment.

PowerShell:

    .venv\Scripts\Activate.ps1

CMD:

    .venv\Scripts\activate


## STEP 3

Install packages:

    python -m pip install --upgrade pip

    pip install -r requirements.txt


# GEMINI API

Create a Gemini API key through Google's AI developer tooling.

Open `.env`.

Set:

    GEMINI_API_KEY=YOUR_API_KEY


The model is configurable:

    GEMINI_MODEL=gemini-2.5-flash


If your account exposes another supported Gemini model,
change the value in `.env`.


# RUN THE APPLICATION

Run:

    python -m uvicorn app.main:app --reload


Open:

    http://127.0.0.1:8000


# API DOCUMENTATION

FastAPI Swagger documentation:

    http://127.0.0.1:8000/docs


Alternative:

    http://127.0.0.1:8000/redoc


# HEALTH CHECK

Open:

    http://127.0.0.1:8000/health


Expected response:

    {
        "status": "ok",
        "application": "PocketSmart AI"
    }


# TESTING

Run:

    pytest -q


# MAIN ROUTES

GET /

GET /login

GET /register

GET /dashboard

GET /planner/home

GET /planner/party

GET /planner/jewelry

GET /history


# AUTH API

POST /api/register

POST /api/login

POST /api/logout

GET /api/session-info

GET /api/session-data


# PLANNER API

POST /api/generate-home

POST /api/generate-party

POST /api/generate-jewelry


# HISTORY API

GET /api/history


# DATABASE

The application automatically creates:

    pocketsmart.db

The database contains:

    users

    recommendations


# IMPORTANT

The application does not pretend to retrieve live product prices from
Amazon, Flipkart, IKEA, Swiggy, Zomato or OYO.

Instead, the AI generates recommendations and the application creates
search links for the relevant platforms.

For production deployment, official or authorized APIs can be integrated
for live product/service information.


# JEWELRY IMAGE

The Jewelry Planner supports an optional image upload.

The image is sent to Gemini as a multimodal input when a valid Gemini
API key is configured.


# FALLBACK MODE

If GEMINI_API_KEY is empty or Gemini returns an error, PocketSmart AI
automatically provides fallback recommendations.

This allows the application to run even before Gemini is configured.