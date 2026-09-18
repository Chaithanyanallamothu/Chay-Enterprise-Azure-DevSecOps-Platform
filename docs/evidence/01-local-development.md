# 01 - Local Development Validation

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Objective

The first checkpoint was to establish a repeatable local development baseline before adding container, CI, security, and Kubernetes controls.

The application is intentionally small. The purpose of the local validation was to prove that the API behavior, tests, linting, and Prometheus instrumentation were stable before moving into the delivery platform.

## Application

The FastAPI service exposes:

    GET  /
    GET  /health
    GET  /ready
    GET  /version
    GET  /api/orders
    POST /api/orders
    GET  /metrics

The order endpoint supports controlled normal, slow, and failure behavior. These execution modes were later reused during observability, load testing, and autoscaling validation.

## Python Compatibility Incident

The first local environment used Python 3.14.7.

During dependency installation, `pydantic-core` failed because the required PyO3 compatibility did not align with the interpreter version being used.

I treated this as a development-runtime compatibility problem rather than changing application behavior to work around the local interpreter.

The development environment was standardized on Homebrew Python 3.12.

Validated interpreter:

    Python 3.12.14

This also aligned local development with the Python 3.12 container runtime.

## Virtual Environment

A clean Python 3.12 virtual environment was created and dependencies were installed from the repository-controlled requirement files.

The final development dependency path uses:

    application/requirements.txt
    application/requirements-dev.txt

## Test Baseline

The regression suite validates:

- liveness
- readiness
- application version
- order retrieval
- successful order creation
- controlled failed-order behavior
- Prometheus instrumentation

Final local result:

    6 tests passed

The test run produced two framework deprecation warnings associated with the FastAPI/Starlette test stack. They did not represent application test failures.

## Linting

Ruff was used as the Python linting control.

Final result:

    Ruff passed

Dependency consistency was also checked successfully.

## Runtime Validation

The API was started locally and validated through its HTTP endpoints.

The validation confirmed:

    /health     -> 200
    /ready      -> 200
    /version    -> 200
    /metrics    -> Prometheus metrics available

Application metrics include:

    chay_http_requests_total
    chay_http_request_duration_seconds
    chay_orders_created_total
    chay_orders_failed_total

## Engineering Outcome

The local checkpoint established:

    Python 3.12 baseline
        |
        v
    Dependency installation
        |
        v
    Unit/regression tests
        |
        v
    Ruff validation
        |
        v
    API runtime validation
        |
        v
    Prometheus metric validation

This became the application baseline used by the container and CI workflows.

## Evidence

Screenshots:

    docs/evidence/screenshots/01-local-development/
    ├── 01-unit-tests-and-lint-passed.png
    └── 02-api-and-prometheus-validation.png

These screenshots capture the validated development baseline rather than a reconstructed test performed after the platform was complete.
