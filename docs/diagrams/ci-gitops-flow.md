# CI, Artifact and GitOps Flow

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

```mermaid
flowchart TD
    PUSH["Git Push"] --> VALIDATE["Azure DevOps Application Validation"]

    VALIDATE --> TEST["Tests + Coverage + Ruff"]
    TEST --> SONAR["SonarQube Quality Gate"]
    SONAR --> SECURITY["Trivy Security Validation"]

    SECURITY --> AGENT["Private Azure DevOps Agent"]
    AGENT --> BUILD["Build Production Image Once"]
    BUILD --> SCAN["Trivy Scan Exact Production Image"]

    SCAN -->|"Pass"| ACR["Push Same Image to Private ACR"]
    SCAN -->|"Fail"| STOP["Stop Pipeline"]

    ACR --> SHA["Immutable Git-SHA Tag"]
    SHA --> DIGEST["Registry Digest"]

    SHA --> HELM["Helm Git Desired State"]
    HELM --> ARGO["Argo CD"]
    ARGO --> AKS["Private AKS"]

    ACR -->|"AcrPull"| AKS

    AKS --> API["FastAPI Deployment"]
    AKS --> HPA["HPA"]
    AKS --> PROM["Prometheus"]
    AKS --> GRAF["Grafana"]

    K6["In-Cluster k6"] --> API
    API -->|"Application Metrics"| PROM
    PROM --> GRAF
    HPA --> API
```

## Delivery Control

The implementation separates four responsibilities:

    Source and Quality
        |
        v
    Artifact Validation
        |
        v
    GitOps Deployment
        |
        v
    Runtime Operations

The production image is built once, scanned, and then pushed as the same artifact.

The artifact uses the Git commit SHA rather than a mutable deployment tag.

A successful CI pipeline does not directly mutate the production Kubernetes workload.

The approved immutable image becomes part of Git desired state, and Argo CD performs reconciliation.
