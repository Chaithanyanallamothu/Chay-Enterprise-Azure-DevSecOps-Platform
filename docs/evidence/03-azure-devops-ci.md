# 03 - Azure DevOps CI Validation

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Objective

Azure DevOps owns continuous integration for this project.

The CI pipeline validates source quality and security, builds the production container on a private agent, scans the exact artifact, and publishes the approved image to private Azure Container Registry.

CI deliberately stops at artifact publication. Argo CD owns deployment.

## Source Integration

GitHub is the source repository.

A push to the configured branch triggers the Azure DevOps CI workflow.

The pipeline definition is maintained in:

    pipelines/azure-pipelines.yml

## Pipeline Stages

The main pipeline is organized into three major stages:

    Application Validation
        |
        v
    Security Validation
        |
        v
    Build / Scan / Publish Artifact

## Application Validation

The application stage uses Python 3.12 and performs:

- dependency installation
- Ruff linting
- pytest
- test-result publication
- coverage publication
- SonarQube Cloud preparation
- SonarQube analysis
- Quality Gate evaluation

Validated coverage:

    94.12%

Validated tests:

    100% passed

## Security Validation

The security stage performs Trivy-based validation before production artifact publication.

The policy focuses on actionable HIGH and CRITICAL findings.

The final remediated state contains zero blocking HIGH/CRITICAL findings under the implemented policy.

## Private Artifact Stage

The production image is built on:

    chay-secure-api-prod-agent-01

Agent pool:

    Private-Azure-Agent-Pool

The private agent validates its required tooling, authenticates through managed identity, builds the production Linux/amd64 image, scans the exact image, pushes that same image to ACR, and queries the resulting registry digest.

## Artifact Integrity

The pipeline uses the Git commit SHA as the image tag.

The build does not publish `latest` as the GitOps artifact.

The production image is built once.

The sequence is:

    Build
      |
      v
    Scan exact local image
      |
      v
    Security gate
      |
      v
    Push same image
      |
      v
    Query registry digest

This prevents a second unscanned rebuild from being substituted after the container security gate.

## Managed Identity

The private agent authenticates to Azure using its system-assigned managed identity.

The identity has the registry publication permission required by the pipeline:

    AcrPush

No ACR administrator password is required by the workflow.

## Final Sonar Enforcement Run

After the initial successful Sonar integration, the configuration was hardened to explicitly make CI wait for the SonarQube Quality Gate:

    sonar.qualitygate.wait=true

The enforcement change was committed as:

    5baf04a
    Enforce SonarQube quality gate in CI

Azure DevOps run:

    #20260918.28

completed successfully using that configuration.

The run showed:

    Application Validation    passed
    Security Validation       passed
    Build/Scan/Publish        passed
    Tests                     100% passed
    Coverage                  94.12%

The run contained Azure-hosted runner migration notices. These were provider notices rather than application or security-stage failures.

## CI/CD Responsibility Boundary

The normal CI pipeline does not execute a direct production deployment.

Its responsibility ends with the validated immutable artifact.

Deployment responsibility continues through:

    ACR Artifact
        |
        v
    Git Desired State
        |
        v
    Argo CD
        |
        v
    AKS

## Evidence

Screenshots:

    docs/evidence/screenshots/03-ci/
    ├── 01-github-source-repository-baseline.png
    ├── 02-azure-devops-ci-validation-passed.png
    └── 03-nonroot-remediation-ci-passed.png

Additional enforced Quality Gate CI evidence:

    docs/evidence/screenshots/04-sonarqube/
    └── 04-enforced-quality-gate-ci-passed.png
