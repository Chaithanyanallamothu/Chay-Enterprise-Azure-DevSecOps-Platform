# 07 - Argo CD GitOps Validation

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Objective

Argo CD owns continuous deployment for the application.

The goal is to keep the deployment authority separate from Azure DevOps CI and make Git the source of Kubernetes desired state.

## Responsibility Boundary

The delivery boundary is:

    Azure DevOps CI
        |
        v
    Validated ACR Artifact
        |
        v
    Git Desired State
        |
        v
    Argo CD
        |
        v
    Private AKS

Azure DevOps does not directly deploy the production application during the normal CI workflow.

## Configuration

GitOps configuration is maintained under:

    argocd/

Application deployment configuration is maintained under:

    helm/chay-demo-api/

The Argo CD application points to the Helm path in the GitHub repository.

## Application Namespace

The application is deployed into:

    chay-devsecops

Monitoring uses:

    monitoring

## Reconciliation

The application uses automated synchronization with:

    prune
    selfHeal

This allows Argo CD to reconcile runtime state toward the Git-defined desired state.

## Argo CD Project Scope

The Argo CD project uses an explicit resource whitelist.

The application requires resources including:

- Deployment
- Service
- ConfigMap
- HorizontalPodAutoscaler

HPA authorization was added deliberately when autoscaling was introduced rather than granting unrestricted resource access.

## Immutable Desired State

The Helm values reference the full immutable image SHA.

Final application image tag:

    cce36ef47e07d29ce3e2641a0e7c0e15514da777

This ties the desired Kubernetes workload to the validated ACR artifact.

## Real GitOps Recovery

The GitOps path exposed two meaningful failures during implementation.

First, an older immutable image referenced by Git was no longer present in ACR.

Second, after the artifact issue was corrected, Kubernetes rejected the named non-root image user under `runAsNonRoot`.

Both problems were corrected through the artifact and Git desired-state path rather than bypassing Argo CD with an ad-hoc production deployment.

The final corrected image was published and referenced through Helm.

Argo CD then reconciled the workload.

## Final Validation

The final GitOps validation confirmed the corrected workload was running and application endpoints were healthy.

The validated application included:

    /health
    /ready
    /version

The GitOps validation also included capacity diagnostics because the shared AKS node had previously been request constrained.

## Monitoring Through GitOps

Prometheus and Grafana configuration is also managed through the repository and Argo CD.

The monitoring application watches:

    monitoring/prometheus/

This keeps permanent monitoring resources under the same desired-state model.

## Evidence Strategy

No dedicated screenshots were captured under a `07-argocd` folder during the original implementation.

I did not create retrospective screenshots and label them as historical evidence.

The GitOps implementation is instead supported by:

- version-controlled Argo CD manifests
- Helm desired state
- Git history
- GitOps validation pipeline history
- incident/recovery evidence
- final runtime validation

Relevant recovery screenshots are stored under:

    docs/evidence/screenshots/12-incident-recovery/

## Outcome

The final deployment ownership model is:

    CI validates and publishes
    Git declares desired state
    Argo CD reconciles
    AKS runs the workload

This boundary remained intact through troubleshooting and recovery.
