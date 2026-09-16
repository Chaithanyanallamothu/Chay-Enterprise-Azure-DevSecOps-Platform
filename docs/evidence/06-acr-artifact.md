# Azure Container Registry Artifact Publication Evidence

**Author:** Chaithanya Nallamothu  
**Role:** Senior DevSecOps Engineer

## Objective

The CI pipeline needs to produce a container artifact that can be promoted toward the private AKS environment without exposing the registry publicly or storing registry credentials in the pipeline.

For this platform, Azure Container Registry is used as the OCI artifact registry. Images are published using the full Git commit SHA rather than a mutable `latest` tag.

## Registry Security Model

The existing Azure Container Registry is configured with public network access disabled and the administrator account disabled.

Artifact publication runs from the private Azure DevOps self-hosted agent. The agent VM authenticates to Azure using its system-assigned managed identity and has `AcrPush` scoped to the registry.

AKS uses its own kubelet identity with `AcrPull`.

This keeps build-time publication permissions separate from runtime image-pull permissions and avoids registry usernames or passwords in the CI pipeline.

## Artifact Build and Security Gate

The deployable container is built on the private Linux x64 Azure DevOps agent.

The pipeline then runs Trivy against that exact image before publication. Fixable HIGH or CRITICAL vulnerabilities cause the task to fail, preventing the image from being pushed.

The successful path is:

```text
Git commit
    |
    v
Application validation
    |
    v
Source and dependency security gates
    |
    v
Private Azure DevOps agent
    |
    v
Production container build
    |
    v
Trivy container vulnerability gate
    |
    v
Managed identity authentication
    |
    v
Private Azure Container Registry
The container that passes the security gate is the same local image subsequently pushed to ACR; CI does not rebuild it between scanning and publication.

Immutable Artifact Identity

Pipeline run #20260916.6 successfully published the production candidate associated with Git commit:

3910d18757cfc07d839de69e078e0dcdc2b0780

Published image:

chaysecureapiprodacr.azurecr.io/chay-enterprise-devsecops/demo-api:3910d18757cfc07d839de69e078e0dcdc2b0780

ACR resolved the published artifact to the OCI digest:

sha256:59ea968e1eee56320fd4db62fded9c3ef7342043a079d999dcd20463cd990f41

The pipeline verifies that ACR returns a digest after the push. A missing digest is treated as a publication failure.

This gives the platform a traceable relationship between source revision, CI execution, container tag, and registry digest.

Validation Result

The artifact publication stage completed successfully on the private Azure DevOps agent.

Validated controls included:

private-agent execution;
managed-identity Azure authentication;
private ACR authentication;
immutable Git-SHA image tagging;
Linux AMD64 container build;
HIGH/CRITICAL container vulnerability gate;
ACR publication;
registry-side digest verification;
private-agent cleanup after publication.

CI stops at artifact publication. It does not directly deploy the container to AKS. Runtime deployment will be controlled separately through GitOps and Argo CD.

Evidence
Azure DevOps Artifact Pipeline

The pipeline run shows Application Validation, Security Validation, and Build/Scan/Publish Artifact completing successfully.

Immutable ACR Artifact Verification

The final verification task records the Git commit SHA, full ACR image reference, and immutable OCI digest returned by the registry.

Engineering Outcome

At this checkpoint the CI boundary is complete:

Source -> Quality -> Security -> Build -> Scan -> Private ACR

Deployment responsibility remains outside CI. The next platform boundary is:

GitOps desired state -> Argo CD -> AKS

This separation allows CI to establish whether an artifact is safe and publishable while GitOps independently controls what version is allowed to run in the cluster.
