# Platform Architecture

**Author:** Chaithanya Nallamothu  
**Role:** Senior DevSecOps Engineer

## Overview

I built this project around a deliberately small FastAPI service so the main focus could remain on the platform surrounding the application: secure CI, immutable artifacts, GitOps deployment, private Kubernetes operations, observability, load testing, autoscaling, and recovery.

The implemented delivery path is:

    Developer
        |
        v
    GitHub
        |
        v
    Azure DevOps CI
        |
        +--> Unit Tests / Ruff
        +--> SonarQube Cloud
        +--> Trivy Security Gates
        |
        v
    Private Azure DevOps Agent
        |
        +--> Production Container Build
        +--> Scan Exact Artifact
        +--> Managed Identity Authentication
        |
        v
    Private Azure Container Registry
        |
        | Immutable Git-SHA Image
        v
    Git Desired State
        |
        v
    Argo CD
        |
        v
    Private AKS
        |
        +--> FastAPI Application
        +--> Horizontal Pod Autoscaler
        +--> Prometheus
        +--> Grafana
        +--> k6 Validation Workloads

The architecture deliberately separates CI from deployment.

Azure DevOps determines whether source and artifacts are acceptable.

Argo CD determines what approved desired state should run in Kubernetes.

## Source Control

GitHub is the source repository for the project.

Application code, pipelines, Helm configuration, Argo CD configuration, monitoring manifests, load tests, and engineering evidence are maintained in the same repository.

Changes to the application flow through Azure DevOps CI before a deployable artifact is published.

Git also holds the desired runtime image version consumed by Argo CD.

## CI Boundary

Azure DevOps owns continuous integration.

The main CI path performs:

    Source
      |
      v
    Python Tests
      |
      v
    Ruff
      |
      v
    SonarQube Analysis
      |
      v
    Security Validation
      |
      v
    Production Container Build
      |
      v
    Container Vulnerability Gate
      |
      v
    Private ACR Publication

The deployable container is built on the private self-hosted Azure DevOps agent.

The production image is scanned before publication.

The same image that passes the container vulnerability gate is pushed to ACR. The pipeline does not rebuild another production image between scanning and publication.

CI stops after artifact publication.

It does not directly deploy the production workload to AKS.

## Artifact Boundary

Azure Container Registry is used as the OCI registry.

The artifact path is:

    chaysecureapiprodacr.azurecr.io/chay-enterprise-devsecops/demo-api:<Git-SHA>

The project does not use `latest` as the deployable image tag.

The current non-root-remediated GitOps artifact is:

    chaysecureapiprodacr.azurecr.io/chay-enterprise-devsecops/demo-api:cce36ef47e07d29ce3e2641a0e7c0e15514da777

Validated digest:

    sha256:219ae166d3dccccd3c39d1212a18aec99bf6ef18bdc52340aa184d2bc6093f5da

This gives the runtime a traceable relationship between source revision, CI execution, registry artifact, Git desired state, and Kubernetes workload.

## Registry Authentication

The Azure DevOps private agent authenticates to Azure using its system-assigned managed identity.

Its registry permission is:

    AcrPush

AKS uses its kubelet identity for runtime image pulls.

Its registry permission is:

    AcrPull

Build-time publication and runtime consumption therefore use separate identities.

The pipeline does not require the ACR administrator account or registry passwords.

## GitOps Boundary

Argo CD owns deployment reconciliation.

The application desired state is maintained under:

    helm/chay-demo-api/
    argocd/

The application is deployed into:

    chay-devsecops

The monitoring components run in:

    monitoring

Argo CD automated synchronization uses:

    prune
    selfHeal

This means Git remains the source of desired deployment state.

Azure DevOps does not compete with Argo CD by directly applying the same application resources during normal delivery.

## Helm Workload

The Helm chart defines:

- immutable image reference
- service configuration
- container port
- replica configuration
- CPU requests and limits
- memory requests and limits
- liveness probe
- readiness probe
- pod security context
- container security context
- HorizontalPodAutoscaler

Current application resource configuration:

    requests:
      cpu: 5m
      memory: 64Mi

    limits:
      cpu: 250m
      memory: 256Mi

The low CPU request is specific to this shared validation environment.

It should not be interpreted as production workload sizing guidance.

## Container Security

The final application image runs using numeric non-root identity:

    UID 10001
    GID 10001

The Kubernetes workload additionally enforces:

    runAsNonRoot: true

    seccompProfile:
      type: RuntimeDefault

    allowPrivilegeEscalation: false

    capabilities:
      drop:
        - ALL

    readOnlyRootFilesystem: true

The numeric runtime identity became necessary after Kubernetes rejected the earlier named `appuser` configuration under `runAsNonRoot`.

## Private AKS

The application runs on an existing private AKS platform.

The Kubernetes API is not expected to be directly reachable from the developer laptop.

Cluster-aware validation therefore runs through the existing private Azure DevOps agent.

I did not change the AKS API to public access for troubleshooting convenience.

The private-cluster model is preserved throughout the project.

## Existing Azure Platform

This project reuses an Azure environment that already existed.

The shared platform provides infrastructure such as:

- private AKS
- private Azure Container Registry
- private networking
- managed identities
- Azure RBAC
- private Azure DevOps self-hosted agent

This repository does not take Terraform ownership of those shared resources.

I deliberately avoided importing an existing environment into another Terraform state solely to make this repository appear self-contained.

The repository owns the workload-specific delivery and runtime configuration rather than the underlying shared platform.

## Runtime Application

The FastAPI application exposes:

    GET  /
    GET  /health
    GET  /ready
    GET  /version
    GET  /api/orders
    POST /api/orders
    GET  /metrics

The order API supports:

    normal
    slow
    fail

These controlled execution paths provide predictable behavior for monitoring, load testing, autoscaling, and failure validation.

## Observability

Prometheus runs inside the Kubernetes environment and scrapes the application `/metrics` endpoint.

Application metrics include:

    chay_http_requests_total
    chay_http_request_duration_seconds
    chay_orders_created_total
    chay_orders_failed_total

Grafana uses Prometheus as its runtime data source.

The runtime dashboard contains:

- API requests per second
- P95 request latency
- P99 request latency
- orders created
- orders failed
- Prometheus target health

I intentionally keep runtime observability separate from build-time quality analysis.

SonarQube remains responsible for source-quality visibility.

Prometheus and Grafana remain responsible for runtime visibility.

## Private Grafana

Grafana remains private inside the Kubernetes environment.

It was not exposed through a public LoadBalancer or ingress just to capture portfolio evidence.

The developer laptop could not directly reach the private dashboard.

The private agent VM also could not directly route to the Kubernetes service CIDR.

The normal Reader identity was not broadened merely to enable port forwarding.

For the final dashboard evidence, I used a temporary in-cluster capture workflow.

The rendered PNG was retrieved through the Azure DevOps execution path and preserved under:

    docs/evidence/screenshots/09-monitoring/07-grafana-runtime-dashboard.png

After evidence collection, the temporary capture workload and retrieval pipeline were removed.

The permanent Prometheus and Grafana configuration remained unchanged.

## Load Testing

k6 runs inside the private Kubernetes environment.

Two scenarios are maintained.

Baseline:

    5 VUs
    60 seconds

Autoscaling:

    40 VUs
    3 minutes

The baseline workload validates normal application behavior.

The autoscaling workload creates controlled CPU pressure to exercise HPA behavior.

Running k6 in-cluster avoids exposing the private application solely for load generation.

## Horizontal Pod Autoscaling

Current HPA configuration:

    minimum replicas: 1
    maximum replicas: 3
    CPU target:       30%

The maximum replica count is intentionally limited for the shared environment.

During controlled k6 validation, the application scaled from one replica to three replicas.

## Capacity Constraints

The first GitOps rollout exposed a scheduling constraint.

The important signal was not high actual node CPU usage.

The node was already close to its allocatable CPU request capacity.

I evaluated adding another node pool, but the available Sweden Central subscription vCPU quota did not provide enough headroom.

Instead of increasing infrastructure cost or changing the shared environment unnecessarily, I right-sized the application request for this validation workload.

This allowed the workload to schedule while preserving its CPU limit.

## Access Model

The normal Azure DevOps private-agent AKS access model is:

    Azure Kubernetes Service Cluster User Role
    Azure Kubernetes Service RBAC Reader

This supports the read-only runtime validation used after bootstrap.

Some controlled bootstrap operations required temporary elevated access.

Those role assignments were removed after the required changes were applied and validated.

Evidence of privilege revocation is retained in the repository.

## Architecture Boundaries

The practical boundaries are:

    Developer / Source
            |
            v
    GitHub
            |
            v
    CI Quality and Security
            |
            v
    Private Build Boundary
            |
            v
    Immutable Artifact Boundary
            |
            v
    GitOps Deployment Boundary
            |
            v
    Private AKS Runtime
            |
            v
    Runtime Observability

Each boundary has a different responsibility.

Crossing one boundary does not automatically grant control over the next.

## Final Diagrams

The final visual documentation will contain two diagrams under:

    docs/diagrams/

The first will show the end-to-end platform architecture.

The second will show the CI, artifact, GitOps, and runtime flow.

The diagrams will be based on the implementation in this repository rather than a generic Azure reference architecture.
