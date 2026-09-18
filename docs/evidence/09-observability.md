# 09 - Runtime Observability Validation

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Objective

The observability layer provides runtime visibility for the application without turning Grafana into a CI or project-management dashboard.

Prometheus collects runtime metrics.

Grafana visualizes operational behavior.

## Architecture

    FastAPI /metrics
          |
          v
    Prometheus
          |
          v
    Grafana

Both components run inside the private Kubernetes environment.

## Lightweight Monitoring Decision

The shared AKS node had already demonstrated CPU-request pressure.

A larger monitoring bundle would have consumed unnecessary capacity for this project.

I therefore used lightweight standalone Prometheus and Grafana deployments rather than a larger monitoring stack.

## Prometheus

Prometheus image:

    prom/prometheus:v3.5.0

Retention:

    6h

The configuration uses small resource requests appropriate for this validation environment.

Prometheus scrapes the FastAPI application.

Validated target state:

    UP = 1

## Application Metrics

The application exposes:

    chay_http_requests_total
    chay_http_request_duration_seconds
    chay_orders_created_total
    chay_orders_failed_total

## Grafana

Grafana image:

    grafana/grafana:11.6.0

Dashboard:

    Chay Demo API - Runtime Observability

Dashboard UID:

    chay-demo-api

Panels include:

- API requests per second
- P95 latency
- P99 latency
- orders created
- orders failed
- Prometheus target health

Refresh interval:

    10 seconds

## Runtime Validation

The monitoring validation checks more than pod readiness.

The workflow validates:

- application health
- application readiness
- Prometheus target
- Prometheus runtime queries
- Grafana health
- Grafana dashboard provisioning

A dedicated in-cluster validator confirmed the application, Prometheus, and Grafana path.

## Prometheus Query Validation

A later runtime query validation observed cumulative application traffic above:

    75,000 requests

At the time of that validation there was no active traffic in the current five-minute query window.

As a result:

    request rate = 0
    P95/P99 = NaN

This was expected Prometheus behavior.

I did not generate artificial traffic solely to make the final dashboard screenshot contain non-zero rate/latency values.

## Private Grafana Constraint

Grafana remains private.

The developer laptop could not directly reach the private service.

The private Azure DevOps VM also could not route directly to the Kubernetes service CIDR for a simple service-IP curl.

The normal Reader identity was not broadened simply to enable pod port forwarding.

## Dashboard Evidence Workflow

For final visual evidence, a temporary in-cluster dashboard capture workflow was created.

The dashboard was rendered inside the private environment.

The PNG was transferred through an Azure DevOps pipeline artifact.

The final file was validated as:

    PNG
    1920 x 1400
    RGBA

The image was stored at:

    docs/evidence/screenshots/09-monitoring/07-grafana-runtime-dashboard.png

After the evidence was captured, the temporary screenshot workload and retrieval workflow were removed from the repository.

Permanent Prometheus and Grafana resources were not removed.

## Final Dashboard State

The retained dashboard screenshot shows:

    RPS              0
    Orders Created   75473
    Orders Failed    0
    Target           1

P95/P99 are blank because there was no active traffic in the five-minute query window at capture time.

That state is intentionally preserved as the real observation.

## Evidence

Screenshots:

    docs/evidence/screenshots/09-monitoring/
    ├── 01-prometheus-gitops-deployment.png
    ├── 02-runtime-validation-pipeline-passed.png
    ├── 03-prometheus-grafana-runtime-ready.png
    ├── 04-in-cluster-monitoring-validation-passed.png
    ├── 05-prometheus-runtime-validation-pipeline-passed.png
    ├── 06-grafana-private-dashboard-validation.png
    └── 07-grafana-runtime-dashboard.png

## Outcome

The final observability model keeps:

    CI quality -> Azure DevOps / SonarQube / Trivy
    Runtime    -> Prometheus / Grafana / Kubernetes

This separation keeps each tool focused on the signals it is intended to provide.
