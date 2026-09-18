# Operations Runbook

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Purpose

This runbook defines the operational validation and troubleshooting path for the Chay Enterprise Azure DevSecOps Platform.

The platform uses GitHub for source control, Azure DevOps for CI, private Azure Container Registry for OCI artifacts, Argo CD for GitOps deployment, private AKS for runtime, and Prometheus/Grafana for observability.

The operational principle is to diagnose problems without bypassing the security and deployment boundaries built into the platform.

## Delivery Flow

The expected production path is:

    GitHub
       |
       v
    Azure DevOps CI
       |
       v
    Tests / Ruff / SonarQube / Trivy
       |
       v
    Private Build Agent
       |
       v
    Build + Scan Exact Image
       |
       v
    Private ACR
       |
       v
    Git Desired State
       |
       v
    Argo CD
       |
       v
    Private AKS

Azure DevOps owns CI.

Argo CD owns CD.

The normal CI workflow does not directly deploy the production workload to AKS.

## CI Validation

When a source change does not produce an artifact, start with the Azure DevOps pipeline.

Confirm:

- application validation passed
- tests passed
- coverage was published
- Ruff passed
- SonarQube analysis completed
- SonarQube Quality Gate passed
- Trivy security validation passed
- production image scan passed
- artifact publication completed

The repository explicitly enables:

    sonar.qualitygate.wait=true

This makes the SonarQube Quality Gate part of the CI decision path.

## Artifact Validation

Production images use the complete Git SHA.

Expected format:

    chaysecureapiprodacr.azurecr.io/chay-enterprise-devsecops/demo-api:<Git-SHA>

When an immutable-image pull fails, verify both:

1. the AKS runtime identity has `AcrPull`
2. the exact immutable image tag exists in ACR

The final validated application artifact is:

    cce36ef47e07d29ce3e2641a0e7c0e15514da777

Digest:

    sha256:219ae166d3dccccd3c39d1212a18aec99bf6ef18bdc52340aa184d2bc6093f5da

## GitOps Validation

If CI and artifact publication are healthy but the application does not update, inspect Git desired state.

Confirm:

- Helm image tag
- repository revision
- namespace
- Argo CD application state
- allowed Kubernetes resource types

Application namespace:

    chay-devsecops

Monitoring namespace:

    monitoring

Avoid bypassing Argo CD with routine direct deployment commands.

## Pod Scheduling

If a pod remains Pending, inspect Kubernetes scheduling events before changing infrastructure.

Check:

- CPU requests
- memory requests
- node allocatable resources
- existing reserved requests
- replica count
- scheduler events

This project encountered a node with relatively low actual CPU utilization but very high CPU request allocation.

Low actual CPU utilization does not necessarily mean Kubernetes has schedulable CPU capacity.

Current application resources:

    requests:
      cpu: 5m
      memory: 64Mi

    limits:
      cpu: 250m
      memory: 256Mi

These values are specific to the shared validation environment.

## Container Startup

If the pod schedules but does not start, inspect:

- image pull status
- container configuration
- Kubernetes events
- security context
- probes

The final container runs as:

    UID 10001
    GID 10001

The workload enforces:

    runAsNonRoot: true

A previous implementation using a named user produced:

    runAsNonRoot and image has non-numeric user (appuser)

The corrected image uses:

    USER 10001:10001

Do not disable `runAsNonRoot` or revert the application to root to resolve this condition.

## Application Health

Validate:

    /health
    /ready
    /version

Liveness and readiness should be evaluated separately.

A running process does not automatically mean the application is ready to receive traffic.

## Prometheus

When runtime metrics are missing, validate:

    Application /metrics
          |
          v
    Prometheus target
          |
          v
    Prometheus query
          |
          v
    Grafana panel

Application metrics include:

    chay_http_requests_total
    chay_http_request_duration_seconds
    chay_orders_created_total
    chay_orders_failed_total

Expected target state:

    UP = 1

A zero request rate is valid when there is no traffic in the selected query window.

P95/P99 can also be empty when there are no recent histogram observations.

## Grafana

Grafana remains private.

Do not create a public LoadBalancer or public ingress solely for troubleshooting or screenshots.

Primary dashboard:

    Chay Demo API - Runtime Observability

Dashboard UID:

    chay-demo-api

Runtime panels include:

- requests per second
- P95 latency
- P99 latency
- orders created
- orders failed
- Prometheus target health

## k6 Baseline

Baseline definition:

    load-tests/baseline.js

Validated scenario:

    5 VUs
    60 seconds

Previously validated result:

    1,190 HTTP requests
    100% checks passed
    0.00% failed requests
    P95 approximately 3.88 ms

This is a platform validation result, not a production capacity benchmark.

## HPA

Current configuration:

    min replicas: 1
    max replicas: 3
    CPU target:   30%

Autoscaling definition:

    load-tests/autoscaling.js

Validated load:

    40 VUs
    3 minutes

Validated scale-out:

    1 -> 2 -> 3 replicas

If HPA does not scale, compare current utilization against the configured target before treating the behavior as a failure.

## Access Model

The private Azure DevOps agent normally uses:

    Azure Kubernetes Service Cluster User Role
    Azure Kubernetes Service RBAC Reader

Temporary elevated access should not become steady-state access.

For a controlled bootstrap operation:

    Grant temporary role
        |
        v
    Perform required operation
        |
        v
    Validate state
        |
        v
    Revoke temporary role
        |
        v
    Confirm Reader-oriented steady state

## Private Network Operations

The developer laptop is not the authoritative execution path for private AKS or private ACR data-plane operations.

Use the private execution path when the target resource is intentionally inaccessible from the public network.

Do not weaken the architecture simply to make a local command succeed.

## Evidence

Operational evidence:

    docs/evidence/

Screenshots:

    docs/evidence/screenshots/

Before capturing evidence, verify that the terminal or portal does not display:

- tokens
- passwords
- private keys
- registry credentials
- service-connection secrets
- kubeconfig credentials

## Recovery Pattern

The preferred recovery sequence is:

    Observe
       |
       v
    Identify failing layer
       |
       v
    Verify assumptions
       |
       v
    Apply smallest justified change
       |
       v
    Revalidate
       |
       v
    Remove temporary access/workarounds
       |
       v
    Preserve evidence

Detailed recovery evidence is maintained in:

    docs/evidence/12-incident-recovery.md
