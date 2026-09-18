# 06 - Azure Container Registry Artifact Validation

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Objective

The artifact stage publishes a traceable, immutable production image to private Azure Container Registry only after the required validation succeeds.

## Registry

Registry:

    chaysecureapiprodacr.azurecr.io

Repository:

    chay-enterprise-devsecops/demo-api

The registry is part of the existing private Azure platform.

## Artifact Naming

The image tag is the complete Git commit SHA.

Format:

    chaysecureapiprodacr.azurecr.io/chay-enterprise-devsecops/demo-api:<Git-SHA>

The GitOps workload does not rely on `latest`.

## Publication Identity

The private Azure DevOps agent authenticates through its system-assigned managed identity.

Publication permission:

    AcrPush

The pipeline does not require the ACR administrator account or registry username/password credentials.

## Runtime Pull Identity

AKS uses its kubelet identity for image consumption.

Runtime permission:

    AcrPull

This separates the identity that publishes artifacts from the identity that consumes them.

## Initial Artifact Evidence

An earlier successful artifact-publication checkpoint used commit:

    3910d18

That artifact was valid at the time of the original CI evidence.

Later, during GitOps validation, the exact older immutable tag referenced by the desired state was no longer present in ACR.

That became a real recovery incident and is documented separately.

The old artifact should therefore be understood as historical pipeline evidence rather than the current runtime artifact.

## Final Runtime Artifact

The final Kubernetes non-root remediation produced commit:

    cce36ef47e07d29ce3e2641a0e7c0e15514da777

Final image:

    chaysecureapiprodacr.azurecr.io/chay-enterprise-devsecops/demo-api:cce36ef47e07d29ce3e2641a0e7c0e15514da777

Validated digest:

    sha256:219ae166d3dccccd3c39d1212a18aec99bf6ef18bdc52340aa184d2bc6093f5da

This is the immutable artifact referenced by the final Helm desired state.

## Build-Scan-Push Integrity

The artifact stage follows:

    Git SHA
      |
      v
    Build production image once
      |
      v
    Trivy scan exact local image
      |
      v
    Security gate passes
      |
      v
    Push same image
      |
      v
    Query ACR digest

The production image is not rebuilt after the final container security scan.

## Private Registry Behavior

The developer laptop is not used as the authoritative ACR data-plane validation path because the registry is private.

Registry validation is performed from the private Azure environment through the self-hosted agent.

This is consistent with the platform's network design.

## Engineering Outcome

The artifact model provides traceability across:

    Git commit
        |
        v
    Azure DevOps build
        |
        v
    ACR image tag
        |
        v
    ACR digest
        |
        v
    Helm desired state
        |
        v
    AKS workload

## Evidence

Screenshots:

    docs/evidence/screenshots/06-acr/
    ├── 01-azure-devops-acr-publish-pipeline-passed.png
    └── 02-acr-immutable-artifact-digest-verified.png

The screenshots capture the artifact-publication control.

The final runtime artifact identity is documented above so the evidence is not misread as claiming the earlier `3910d18` artifact is still the deployed image.
