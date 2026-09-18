# 08 - Private AKS Deployment Validation

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Objective

The application runs on an existing private AKS platform.

The validation objective was to prove that the GitOps-managed workload could run securely and reliably without changing the cluster to public access.

## Private Cluster

The AKS API is private.

The developer Mac is not expected to directly reach the Kubernetes API endpoint.

Cluster-aware operations are therefore performed from the private Azure DevOps agent.

This architecture was retained even when private access made troubleshooting more complicated.

## Namespace

Application namespace:

    chay-devsecops

Monitoring namespace:

    monitoring

## Workload Security

The final application pod enforces:

    runAsNonRoot: true

    seccompProfile:
      type: RuntimeDefault

    allowPrivilegeEscalation: false

    capabilities:
      drop:
        - ALL

    readOnlyRootFilesystem: true

The container image declares:

    USER 10001:10001

## Health and Readiness

The application exposes:

    /health
    /ready

These endpoints are used by Kubernetes liveness and readiness probes.

The final GitOps validation confirmed the application health, readiness, and version endpoints.

## Resource Configuration

Final application resources:

    requests:
      cpu: 5m
      memory: 64Mi

    limits:
      cpu: 250m
      memory: 256Mi

The small CPU request is specific to this shared validation environment.

## Scheduling Incident

The first rollout encountered insufficient schedulable CPU.

The important distinction was:

    actual node CPU usage != CPU requests already reserved

The node was already close to its allocatable CPU request capacity.

The application therefore remained Pending even though the node did not appear computationally saturated from actual CPU usage alone.

## Node-Pool Evaluation

A dedicated user node pool was considered.

The attempt was blocked by the available Sweden Central vCPU quota.

Rather than adding unnecessary infrastructure or changing the shared platform, the demo workload was right-sized.

The CPU request was reduced in controlled steps until the workload could schedule.

## Non-Root Runtime Incident

After the scheduling and artifact issues were addressed, Kubernetes reported:

    runAsNonRoot and image has non-numeric user (appuser)

The image was corrected to numeric UID/GID `10001:10001`, rebuilt through CI, scanned, published to ACR, referenced through Git desired state, and reconciled through Argo CD.

## ACR Pull

AKS uses its kubelet identity with:

    AcrPull

The final image is:

    chaysecureapiprodacr.azurecr.io/chay-enterprise-devsecops/demo-api:cce36ef47e07d29ce3e2641a0e7c0e15514da777

Digest:

    sha256:219ae166d3dccccd3c39d1212a18aec99bf6ef18bdc52340aa184d2bc6093f5da

## Steady-State Access

The private Azure DevOps agent normally operates with:

    Azure Kubernetes Service Cluster User Role
    Azure Kubernetes Service RBAC Reader

Temporary elevated access used for controlled bootstrap changes was revoked afterward.

## Evidence Strategy

No dedicated `08-aks` screenshot set was captured during the original implementation.

I have not manufactured retrospective evidence.

The AKS state is supported by:

- Helm configuration
- Argo CD configuration
- GitOps validation pipeline history
- monitoring validation
- HPA validation
- incident/recovery screenshots

Relevant recovery evidence:

    docs/evidence/screenshots/12-incident-recovery/
    ├── 01-gitops-recovery-running.png
    └── 02-temporary-cluster-admin-revoked.png

## Outcome

The final workload runs through the intended private path:

    Git
      |
      v
    Argo CD
      |
      v
    Private AKS
      |
      v
    Numeric non-root application
      |
      v
    Private runtime monitoring
