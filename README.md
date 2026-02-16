# Credit Approval System

This repository contains the backend implementation for a Credit Approval System. The system manages customer data, loan applications, and automated credit eligibility assessments based on historical financial data. It is built using Django and Django Rest Framework (DRF), with PostgreSQL as the persistence layer.

---

## Project Structure

```bash
credit_system/
├── backend/
│   ├── backend/          # Project configuration
│   │   ├── settings.py   # Django settings
│   │   ├── urls.py       # Main URL routing
│   │   └── wsgi.py       # WSGI entry point
│   ├── customers/        # Customer management app
│   │   ├── models.py     # Customer database models
│   │   ├── serializers.py# DRF serializers
│   │   ├── services.py   # Business logic (Ingestion)
│   │   ├── views.py      # API views
│   │   ├── urls.py       # App-specific URL routing
│   │   └── test/         # Unit tests
│   ├── loan/             # Loan management app
│   │   ├── models.py     # Loan database models
│   │   ├── serializers.py# DRF serializers
│   │   ├── services.py   # Business logic (Credit scoring)
│   │   ├── views.py      # API views
│   │   ├── urls.py       # App-specific URL routing
│   │   └── test/         # Unit tests
│   └── manage.py         # Django management script
├── data/                 # Data ingestion source files
│   ├── customer_data.xlsx
│   └── loan_data.xlsx
├── Dockerfile            # Application container definition
├── compose.yaml          # Docker Compose configuration
├── requirements.txt      # Python dependencies
├── .env_example          # Environment variable template
└── README.md             # Project documentation
```

## Environment Configuration

To configure the application environment, duplicate the provided example configuration file and update the variables as necessary.

```bash
cp .env_example .env
```

### Configuration Variables

The application requires the following environment variables:

*   **Database Credentials**:
    *   `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: Configuration for the PostgreSQL container.
    *   `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Configuration for the Django application to connect to the database.
*   **Application Settings**:
    *   `SECRET_KEY`: The cryptographic signing key for the Django application.
    *   `DEBUG`: Boolean flag to enable/disable debug mode (e.g., `True` or `False`).

---

## API Documentation

The application exposes the following RESTful endpoints:

### 1. Register Customer
*   **Endpoint**: `/api/register/`
*   **Method**: `POST`
*   **Description**: Registers a new customer entity and calculates their initial credit limit.
*   **Payload**:
    ```json
    {
      "first_name": "string",
      "last_name": "string",
      "age": "integer",
      "monthly_salary": "decimal",
      "phone_number": "string"
    }
    ```
*   **Response**: Returns the registered customer details including the calculated `approved_limit`.

### 2. Loan Eligibility Assessment
*   **Endpoint**: `/api/check-eligibility/`
*   **Method**: `POST`
*   **Description**: Evaluates a customer's eligibility for a specific loan request based on their credit score and financial history.
*   **Payload**:
    ```json
    {
      "customer_id": "integer",
      "loan_amount": "decimal",
      "interest_rate": "decimal",
      "tenure": "integer"
    }
    ```
*   **Response**: Returns approval status, mathematically corrected interest rate, monthly installment amount, and a descriptive message.

### 3. Create Loan
*   **Endpoint**: `/api/create-loan/`
*   **Method**: `POST`
*   **Description**: Processes a loan application. If the eligibility criteria are met, a new loan record is persisted in the database.
*   **Payload**: Same structure as the Eligibility Assessment endpoint.
*   **Response**: Returns the created Loan ID and final approval details.

### 4. Retrieve Loan Details
*   **Endpoint**: `/api/view-loan/<loan_id>`
*   **Method**: `GET`
*   **Description**: Retrieves detailed information for a specific loan.
*   **Response**: Customer profile, loan principal, interest rate, EMI, and tenure.

### 5. List Customer Loans
*   **Endpoint**: `/api/view-loans/<customer_id>`
*   **Method**: `GET`
*   **Description**: Retrieves a comprehensive list of all active loans associated with a specific customer.
*   **Response**: Array of active loan objects including repayment status.

---

## Business Logic and Architecture

### Credit Scoring Algorithm
The system implements a proprietary algorithm to determine a credit score (0-100) based on the following factors:
1.  **Repayment History**: Analysis of timely payments on previous obligations.
2.  **Loan Frequency**: Impact of multiple loan applications within the current calendar year.
3.  **Loan Volume**: Assessment of the current loan amount relative to the customer's approved limit.
4.  **Debt-to-Income Ratio**: Verification that the sum of current EMIs and the proposed EMI does not exceed 50% of the customer's monthly income.
5.  **Data Ingestion Constraints**: Validation against the customer's pre-calculated `approved_limit`.

### Interest Rate Adjustment
Interest rates are dynamically adjusted based on the calculated credit score:
*   **Score > 50**: Approved at the requested interest rate.
*   **50 >= Score > 30**: Minimum applicable interest rate is 12%.
*   **30 >= Score > 10**: Minimum applicable interest rate is 16%.
*   **Score <= 10**: Application rejected.

### Approved Limit Calculation
Upon registration, a customer's credit limit is formulaically determined as:
$$ Limit = \text{Round}\left(36 \times \text{Monthly Salary}, 100,000\right) $$

---

## Data Ingestion Strategy

The system is designed with an automated data ingestion pipeline.

### Docker Environment
When executed via `docker compose`, a dedicated **worker service** is initialized. This service monitors the database availability and performs the following initialization tasks:
1.  Executes database migrations.
2.  Ingests customer data from `data/customer_data.xlsx`.
3.  Ingests loan data from `data/loan_data.xlsx`.

This architecture ensures that the application is fully seeded and operational immediately upon startup.

### Manual Execution (Local Development)
For local development environments not utilizing the containerized worker, data ingestion can be triggered manually via Django management commands:

```bash
python manage.py ingest_data
python manage.py ingest_loan
```

---

## Installation and Execution

### Prerequisites
*   Python 3.8 or higher
*   Docker & Docker Compose (optional, recommended for production-like environments)

### Method 1: Docker Compose (Recommended)
Build and deploy the application container stack. This includes the application server, PostgreSQL database, and the data ingestion worker.

```bash
docker compose up --build
```

The API will be accessible at `http://localhost:8000`.

### Method 2: Local Installation
1.  **Environment Setup**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```
2.  **Dependency Installation**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Database Migration**:
    ```bash
    cd backend
    python manage.py migrate
    ```
4.  **Service Startup**:
    ```bash
    python manage.py runserver
    ```
    The API will be accessible at `http://127.0.0.1:8000`.

---

## Testing

## Testing

Unit tests for each API endpoint have been implemented using `pytest` and `django.test`. These tests ensure the reliability of the business logic and API contracts.

### Test Coverage

*   **Customer Registration** (`/register`):
    *   Verifies successful customer creation with valid payload.
    *   Checks correct persistence of personal and financial data.
    *   Ensures `approved_limit` is correctly calculated upon registration.

*   **Loan Eligibility** (`/api/check-eligibility/`):
    *   **Approved Flow**: Validates that a creditworthy customer (high income/limit) receives an approval with corrected interest rate and EMI details.
    *   **Rejection Flow**: Ensures appropriate response structures when eligibility criteria (e.g., loan amount > limit) are not met.

*   **Loan Creation** (`/api/create-loan/`):
    *   **Success**: Confirms that a loan is successfully created and persisted in the database for eligible requests, returning a valid `loan_id`.
    *   **Error Handling**: Verifies 404 response when attempting to create a loan for a non-existent customer.

*   **View Loan Actions**:
    *   **Single Loan** (`/api/view-loan/<loan_id>`): Tests retrieval of specific loan details, including customer and repayment info. Verifies 404 for invalid loan IDs.
    *   **Customer Loans** (`/api/view-loans/<customer_id>`): Validates retrieval of all loans associated with a customer. effectively handling cases with multiple loans or zero active loans.

### Running Tests in Docker

To run the complete test suite inside the running Docker container, execute:

```bash
docker exec -it django-container pytest
```

