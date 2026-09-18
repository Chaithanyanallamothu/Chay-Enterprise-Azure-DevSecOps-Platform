# Security Model

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Scope

This document describes the security controls implemented by the application delivery and Kubernetes workload in this repository.

The underlying Azure environment is shared existing infrastructure.

This repository does not claim ownership of the AKS cluster, Azure networking, or Azure Container Registry infrastructure.

## Source Boundary

GitHub is the source repository.

The repository contains:

- application code
- tests
- Docker configuration
- Azure DevOps pipelines
- Helm configuration
- Argo CD configuration
- monitoring configuration
- load tests
- engineering evidence

Secrets and private credentials should not be committed to the repository.

## CI Security Boundary

Azure DevOps performs validation before the production artifact is published.

The implemented CI controls include:

- Python unit tests
- Ruff linting
- SonarQube Cloud analysis
- Trivy security scanning
- production container scanning
- artifact publication only after successful validation

The production image is scanned before ACR publication.

The image is not rebuilt between the final container scan and push.

## Vulnerability Policy

Trivy is used for vulnerability validation.

The blocking policy focuses on fixable:

    HIGH
    CRITICAL

findings.

Unfixed findings are excluded from this specific blocking policy.

The initial application image produced:

    Debian HIGH:       9
    Debian CRITICAL:   3
    Python HIGH:       3

    Total blocking:   15

After remediation:

    Debian HIGH/CRITICAL: 0
    Python HIGH/CRITICAL: 0

    Total blocking:       0

Security remediation is followed by functional regression testing.

## Container Identity

The final application image runs with:

    UID 10001
    GID 10001

The numeric identity allows Kubernetes to validate the `runAsNonRoot` policy deterministically.

The earlier named non-root identity was replaced after Kubernetes rejected it under the non-root policy.

## Kubernetes Container Controls

The application applies:

    runAsNonRoot: true

    seccompProfile:
      type: RuntimeDefault

    allowPrivilegeEscalation: false

    capabilities:
      drop:
        - ALL

    readOnlyRootFilesystem: true

The application also uses explicit resource requests and limits.

## Health Controls

The application exposes separate endpoints for:

    /health
    /ready

Kubernetes uses these for liveness and readiness validation.

Separating readiness from liveness allows Kubernetes to distinguish whether the process is alive from whether it is ready to receive application traffic.

## Registry Security

Azure Container Registry is used as the private OCI registry.

Artifact publication uses:

    Private Azure DevOps Agent
        |
        | System-Assigned Managed Identity
        | AcrPush
        v
    Azure Container Registry

Runtime image consumption uses:

    AKS Kubelet Identity
        |
        | AcrPull
        v
    Azure Container Registry

The publisher and consumer therefore use separate identities.

The pipeline does not depend on ACR administrator credentials.

## Immutable Artifact Identity

Production artifacts are tagged using the complete Git commit SHA.

Example:

    chaysecureapiprodacr.azurecr.io/chay-enterprise-devsecops/demo-api:cce36ef47e07d29ce3e2641a0e7c0e15514da777

Validated digest:

    sha256:219ae166d3dccccd3c39d1212a18aec99bf6ef18bdc52340aa184d2bc6093f5da

Mutable `latest` tagging is not used for the GitOps workload.

## Deployment Security Boundary

The main Azure DevOps CI pipeline does not directly deploy the production application to AKS.

The responsibility boundary is:

    Azure DevOps
        |
        v
    Validated Artifact
        |
        v
    Git Desired State
        |
        v
    Argo CD
        |
        v
    AKS

This prevents the normal artifact-publication path from also becoming a second Kubernetes deployment controller.

## Private Kubernetes API

AKS uses a private API endpoint.

The developer laptop is not expected to directly administer the cluster.

Cluster-aware validation is performed through the existing private Azure DevOps agent.

The Kubernetes API was not made public for troubleshooting convenience.

## AKS Access Model

The steady-state private-agent access is limited to:

    Azure Kubernetes Service Cluster User Role
    Azure Kubernetes Service RBAC Reader

This supports the read-only validation required after bootstrap.

The Reader identity is not intended for:

- arbitrary pod creation
- arbitrary `kubectl exec`
- pod port forwarding
- cluster administration

## Controlled Privilege Elevation

Some bootstrap operations required temporary elevated access.

The elevation was used for the specific configuration change and then revoked.

Evidence of the final privilege state is maintained under:

    docs/evidence/screenshots/11-autoscaling/
    docs/evidence/screenshots/12-incident-recovery/

Temporary administrative access is not treated as part of the steady-state pipeline identity.

## Argo CD Scope

Argo CD uses a project-level resource whitelist.

The project is not given unrestricted permission for every possible Kubernetes resource type.

When HPA support was introduced, the required:

    autoscaling/HorizontalPodAutoscaler

resource type was added deliberately.

This keeps GitOps authorization aligned with the resources actually required by the project.

## Namespace Separation

Application namespace:

    chay-devsecops

Monitoring namespace:

    monitoring

The application and observability workloads are therefore logically separated.

## Runtime Monitoring Security

Prometheus and Grafana remain inside the private Kubernetes environment.

Grafana was not exposed publicly for demonstration or screenshot purposes.

When final dashboard evidence was required, it was captured inside the private environment and retrieved through the Azure DevOps execution path.

The temporary capture resources were removed afterward.

## Managed Identity

The private Azure DevOps VM uses its system-assigned managed identity for Azure authentication.

This reduces dependence on long-lived Azure credentials in pipeline configuration.

The identity is granted only the Azure permissions required for its workflow.

## Secrets

The repository should not contain:

- Azure account passwords
- ACR administrator credentials
- Azure DevOps personal access tokens
- SonarQube tokens
- kubeconfig credentials
- private keys
- service-connection secrets

External service credentials belong in their respective secured connection mechanisms.

## Security Gate Philosophy

The project uses several independent controls instead of treating one scanner as the complete security model.

The delivery path includes:

    Source Validation
          |
          v
    Quality Analysis
          |
          v
    Dependency / Source Security
          |
          v
    Production Container Build
          |
          v
    Container Vulnerability Gate
          |
          v
    Private Artifact Publication
          |
          v
    GitOps Deployment
          |
          v
    Restricted Kubernetes Runtime

A successful control at one stage does not remove the need for the next stage.

For example, a clean vulnerability scan does not replace regression testing.

Likewise, a successfully published container does not automatically authorize deployment.

## Runtime Security vs Build Security

Build-time controls include:

    Azure DevOps
    SonarQube
    Trivy
    ACR artifact verification

Runtime controls include:

    Kubernetes security context
    private AKS
    Argo CD
    resource controls
    health/readiness probes
    Prometheus
    Grafana
    HPA
    restricted AKS access

These controls address different parts of the delivery lifecycle.

## Security Evidence

Evidence is maintained throughout:

    docs/evidence/screenshots/

Relevant categories include:

    03-ci
    04-sonarqube
    05-security
    06-acr
    11-autoscaling
    12-incident-recovery

The repository keeps evidence of both successful controls and meaningful remediation where the failure changed the final design.
