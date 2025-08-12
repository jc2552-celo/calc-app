# Calc App

A FastAPI-based calculator service with reports, metrics, and history tracking.  
Features include:
- REST API endpoints for calculations and reports.
- Static HTML report page.
- SQLite database integration via SQLAlchemy.
- Unit, integration, and end-to-end tests.
- Dockerized for easy deployment.
- CI/CD with GitHub Actions: automatic tests, build, and push to Docker Hub.

---

## 📦 Run Locally

### Requirements
- Python 3.12+
- [Poetry](https://python-poetry.org/) or `pip`
- SQLite (bundled with Python)
- Node.js (only for Playwright E2E tests)

### Setup
```bash
git clone git@github.com:jc2552-celo/calc-app.git
cd calc-app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

Start the Server
uvicorn app.main:app --reload
http://127.0.0.1:8000/static/report.html

 Run Tests
Unit + Integration
pytest -q


End-to-End (Playwright)
pytest -k e2e -q

Run with Docker
Pull from Docker Hub
docker pull jaysocodi/calc-app:latest
docker run --rm -p 8000:8000 jaysocodi/calc-app:latest
http://127.0.0.1:8000/static/report.html

Development with Docker Compose
services:
  calc-app:
    image: jaysocodi/calc-app:latest
    ports:
      - "8000:8000"

Run:
docker compose up -d
docker compose down

Continuous Integration

    GitHub Actions Workflow: .github/workflows/ci.yml

        Runs unit, integration, and E2E tests.

        Builds Docker image.

        Pushes latest image to Docker Hub:
        https://hub.docker.com/r/jaysocodi/calc-app

API Endpoints
Method	Endpoint	Description
GET	/history	Get calculation history
POST	/calculate	Perform a calculation
GET	/reports/metrics	Get usage metrics
GET	/reports/recent?limit=10	Get recent calculation report

https://github.com/jc2552-celo/calc-app
https://hub.docker.com/r/jaysocodi/calc-app
