# Restful Booker API Test Automation Framework

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Pytest](https://img.shields.io/badge/Pytest-8.3-green?logo=pytest)
![Allure](https://img.shields.io/badge/Allure-Report-orange)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-black?logo=github)
![Docker](https://img.shields.io/badge/Docker-Supported-blue?logo=docker)

Enterprise-grade API test automation framework for the [Restful Booker API](https://restful-booker.herokuapp.com/apidoc/index.html), built with Python, Pytest, and Allure reporting.

---

## Features

- **Functional CRUD Tests** — Full coverage for Create, Read, Update, Partial Update, Delete
- **Authentication Tests** — Token-based auth with positive and negative scenarios
- **Contract Testing** — JSON Schema validation for all API responses
- **Negative & Security Testing** — Invalid inputs, missing fields, SQL injection, XSS, path traversal
- **E2E Workflow Tests** — Complete booking lifecycle and search workflows
- **Performance Testing** — Response time assertions for all endpoints
- **Boundary Testing** — Edge cases for prices, name lengths, dates, and invalid IDs
- **Idempotency Testing** — Verifying PUT idempotency and GET consistency
- **Header Validation** — Content-Type, sensitive header exposure checks
- **Data-Driven Testing** — Parametrized tests with external JSON test data
- **Pydantic Response Validation** — Automatic response structure validation via data models
- **Allure Reporting** — Interactive reports with steps, attachments, and severity levels
- **CI/CD Pipeline** — GitHub Actions with matrix testing (Python 3.11 & 3.12)
- **Docker Support** — Containerized test execution
- **Multi-Environment Config** — Configurable via .env files per environment
- **Structured Logging** — Request/response logging with configurable levels
- **Retry Logic** — Exponential backoff for transient failures

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11+ | Programming language |
| Pytest | Test framework |
| Requests | HTTP client |
| Pydantic | Data models & validation |
| JSON Schema | Contract testing |
| Allure | Test reporting |
| Faker | Test data generation |
| GitHub Actions | CI/CD pipeline |
| Docker | Containerized execution |
| Flake8 / Black / isort | Code quality |

---

## Project Structure

```
restful-booker-api-framework/
├── .github/workflows/       # CI/CD pipeline
├── api_clients/             # HTTP client layer
│   ├── base_client.py       # Base HTTP client with logging
│   ├── auth_client.py       # Authentication endpoints
│   └── booking_client.py    # Booking CRUD endpoints
├── config/                  # Environment configuration
│   ├── config.py            # Settings loader
│   └── environments/        # Per-environment .env files
├── models/                  # Pydantic data models
├── schemas/                 # JSON Schemas for contract tests
├── test_data/               # External test data (JSON)
├── tests/
│   ├── test_auth/           # Authentication tests
│   ├── test_bookings/       # CRUD functional tests
│   ├── test_contracts/      # Schema validation tests
│   ├── test_e2e/            # End-to-end workflow tests
│   └── test_negative/       # Error handling & security tests
├── utils/                   # Helpers, logger, validators
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── pytest.ini
```

---

## Quick Start

### Local Setup

```bash
# Clone the repository
git clone https://github.com/Nikolay-Chillev/restful-booker-api-framework.git
cd restful-booker-api-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest -v --alluredir=allure-results
```

### Docker

```bash
# Run all tests
docker-compose up --build api-tests

# Run smoke tests only
docker-compose up --build smoke-tests
```

---

## Running Tests

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make smoke` | Run smoke tests only |
| `make regression` | Run regression tests |
| `make contract` | Run contract/schema tests |
| `make negative` | Run negative tests |
| `make e2e` | Run E2E workflow tests |
| `make report` | Generate & open Allure report |
| `make lint` | Run code quality checks |
| `make format` | Auto-format code with Black & isort |

### Pytest Markers

```bash
pytest -m smoke          # Quick smoke tests
pytest -m regression     # Full regression suite
pytest -m negative       # Negative/error handling tests
pytest -m contract       # JSON Schema contract tests
pytest -m e2e            # End-to-end workflows
pytest -m performance    # Response time assertions
pytest -m boundary       # Boundary value tests
pytest -m headers        # HTTP header validation
pytest -m idempotency    # Idempotency verification
```

---

## Test Categories & Coverage

| Category | Tests | Description |
|----------|-------|-------------|
| Authentication | 8 | Token creation, invalid/empty credentials (parametrized) |
| Create Booking | 11 | Valid creation, field matching, data-driven, deposit variations |
| Get Booking | 6 | Get by ID, filters, 404, response structure |
| Update Booking | 4 | Full update, persistence, auth, non-existent |
| Partial Update | 4 | Single/multi field, auth, field preservation |
| Delete Booking | 4 | Delete, verify 404, auth, non-existent |
| Contract Tests | 4 | JSON Schema validation for all endpoints |
| Negative Tests | 12 | Missing fields, invalid types, SQL injection, XSS, path traversal |
| E2E Workflows | 3 | Full lifecycle, search, rapid update |
| Performance | 5 | Response time assertions for all endpoints |
| Boundary | 11 | Price limits, name lengths, date edges, invalid IDs |
| Headers | 4 | Content-Type, sensitive headers, server info |
| Idempotency | 3 | PUT idempotency, GET consistency, DELETE behavior |
| **Total** | **89** | |

---

## Allure Reporting

Generate and view the interactive Allure report:

```bash
# Generate results during test run
pytest -v --alluredir=allure-results

# Open the report
allure serve allure-results
```

The report includes:
- Test execution overview with pass/fail/skip counts
- Detailed test steps with request/response attachments
- Severity-based categorization (Blocker, Critical, Normal)
- Epic/Feature/Story hierarchy for organized navigation
- Environment information

---

## CI/CD Pipeline

The GitHub Actions workflow runs on every push to `main` and on pull requests:

1. **Matrix testing** across Python 3.11 and 3.12
2. **Smoke tests** run first as a gate
3. **Full regression suite** follows
4. **Allure results** uploaded as artifacts (14-day retention)
5. **Pip caching** for faster builds

---

## Configuration

Environment settings are loaded from `.env` files in `config/environments/`:

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `https://restful-booker.herokuapp.com` | API base URL |
| `AUTH_USERNAME` | `admin` | Auth username |
| `AUTH_PASSWORD` | `password123` | Auth password |
| `REQUEST_TIMEOUT` | `30` | Request timeout (seconds) |
| `RETRY_ATTEMPTS` | `3` | Max retry attempts |
| `LOG_LEVEL` | `INFO` | Logging level |

Switch environments:
```bash
TEST_ENV=staging pytest -v
```

---

## Architecture

```
┌──────────────────────────────────────────────┐
│                  Test Layer                   │
│  (test_auth, test_bookings, test_contracts,  │
│   test_e2e, test_negative, test_performance) │
├──────────────────────────────────────────────┤
│              Fixtures Layer                   │
│  (conftest.py — shared fixtures & setup)     │
├──────────────────────────────────────────────┤
│             API Client Layer                  │
│  (AuthClient, BookingClient ← BaseClient)    │
├──────────────────────────────────────────────┤
│             Models Layer                      │
│  (Pydantic: Booking, BookingResponse, Auth)  │
├──────────────────────────────────────────────┤
│             Utilities Layer                   │
│  (logger, helpers, schema_validator, retry)  │
├──────────────────────────────────────────────┤
│           Configuration Layer                 │
│  (Settings, environment .env files)          │
└──────────────────────────────────────────────┘
```

