# AthletiQ

AthletiQ is a responsive Flask foundation for a professional multi-league sports analytics platform. This first milestone includes the application architecture and interface only; sports data, persistence, search, and authentication are intentionally not implemented yet.

## Tech stack

- Python 3 and Flask
- Flask Blueprints and Jinja2
- Bootstrap 5, custom CSS, and vanilla JavaScript
- Environment-based configuration
- Gunicorn for Render deployment

## Run locally

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   ```

2. Install dependencies and create local configuration:

   ```bash
   pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

3. Start the app:

   ```bash
   flask --app app.py run --debug
   ```

Open `http://127.0.0.1:5000`.

## Render deployment

Create a new Render Web Service connected to this repository and use:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn 'app:create_app()'`
- Environment variable: `SECRET_KEY` with a secure random value

## Architecture

The app factory in `app/__init__.py` creates and configures Flask. Each major feature owns a Blueprint in `app/routes`. Future external sports integrations belong in `app/services`, while future domain objects belong in `app/models`. Templates and static assets remain presentation-only.
