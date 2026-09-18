# End-to-End Platform Architecture

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

```mermaid
flowchart LR
    DEV["Developer"] --> GH["GitHub Repository"]

    subgraph CI["Azure DevOps CI"]
        VALIDATE["Tests + Ruff<br/>SonarQube Quality Gate"]
        SECURITY["Trivy Security Gates"]
        AGENT["Private Self-Hosted Agent"]
        BUILD["Build Production Image"]
        SCAN["Scan Exact Image"]
    end

    GH --> VALIDATE
    VALIDATE --> SECURITY
    SECURITY --> AGENT
    AGENT --> BUILD
    BUILD --> SCAN

    subgraph AZURE["Private Azure Platform"]
        ACR["Azure Container Registry<br/>Immutable Git-SHA Artifact"]
        AKS["Private AKS"]
    end

    SCAN -->|"Managed Identity / AcrPush"| ACR

    GH --> DESIRED["Helm + Git Desired State"]
    DESIRED --> ARGO["Argo CD"]
    ARGO --> AKS
    ACR -->|"Kubelet Identity / AcrPull"| AKS

    subgraph RUNTIME["AKS Runtime"]
        API["FastAPI<br/>Non-Root UID 10001"]
        HPA["Horizontal Pod Autoscaler"]
        PROM["Prometheus"]
        GRAF["Grafana"]
        K6["k6 Validation"]
    end

    AKS --> API
    AKS --> HPA
    AKS --> PROM
    AKS --> GRAF
    AKS --> K6

    API -->|"/metrics"| PROM
    PROM --> GRAF
    HPA --> API
    K6 --> API
```

## Responsibility Boundaries

Azure DevOps owns continuous integration, source validation, security gates, and production artifact publication.

Argo CD owns Kubernetes deployment reconciliation.

AKS consumes the validated immutable image from private ACR using the kubelet identity.

Prometheus and Grafana provide runtime observability.

k6 executes inside the private Kubernetes environment.

The normal CI workflow does not directly deploy the production application to AKS.
