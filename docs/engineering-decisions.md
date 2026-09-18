# Engineering Decisions

**Author:** Chaithanya Nallamothu  
**Role:** Senior DevSecOps Engineer

## Purpose

This document records decisions that materially changed the platform while I was building and validating it.

It is intentionally focused on decisions that came from the implementation rather than generic DevOps recommendations.

## Azure DevOps Owns CI and Argo CD Owns CD

I kept artifact production and runtime reconciliation as separate responsibilities.

Azure DevOps validates:

- application behavior
- code quality
- security
- container artifact

Argo CD reconciles:

- approved Git desired state
- Helm configuration
- Kubernetes runtime

The normal CI pipeline therefore stops at artifact publication.

It does not directly deploy the production workload to AKS.

This avoids creating two deployment authorities for the same Kubernetes application.

## Use Immutable Git-SHA Artifacts

The production artifact uses the complete Git commit SHA as the image tag.

Example:

    chaysecureapiprodacr.azurecr.io/chay-enterprise-devsecops/demo-api:cce36ef47e07d29ce3e2641a0e7c0e15514da777

I avoided using `latest`.

This became especially useful during GitOps troubleshooting because I could verify whether the exact artifact referenced by Git existed in ACR.

## Scan the Exact Artifact That Is Published

The private Azure DevOps agent builds the production container once.

Trivy scans that exact local image.

Only after the image passes the security policy is it pushed to ACR.

I did not rebuild the image after scanning.

Rebuilding between security validation and publication would introduce an unnecessary difference between the artifact that passed the gate and the artifact that was published.

## Use Managed Identity Instead of Registry Credentials

The private build agent authenticates to Azure through its system-assigned managed identity.

It receives:

    AcrPush

AKS uses its kubelet identity with:

    AcrPull

This keeps publication and consumption permissions separate.

It also avoids storing registry usernames or passwords in the CI configuration.

## Keep AKS Private

The Kubernetes API is private.

When the developer laptop could not reach the cluster, I moved cluster-aware validation to the private Azure DevOps agent instead of changing AKS to public access.

The architecture should not become weaker simply because a troubleshooting path is more convenient from a laptop.

## Reuse Existing Azure Infrastructure Without Creating Competing Terraform Ownership

The Azure platform already existed before this workload.

I did not import the shared AKS cluster, networking, registry, and supporting resources into another Terraform state.

That would create competing infrastructure ownership and unnecessary risk to resources used outside this repository.

The project therefore documents its dependency on the existing platform rather than pretending the repository provisioned infrastructure that it did not create.

## Standardize on Python 3.12

Local development initially used Python 3.14.7.

During dependency installation, `pydantic-core` failed because the relevant PyO3 support did not align with that interpreter version.

I standardized local development on Python 3.12 instead of maintaining a local compatibility workaround.

That also aligned development with the Python 3.12 container base.

## Treat Fixable HIGH and CRITICAL Findings as Blocking

The initial application image contained fixable HIGH and CRITICAL findings across the Debian and Python layers.

The security policy for this project focuses on:

    HIGH
    CRITICAL

with unfixed findings excluded from this particular blocking gate.

The objective is to block artifacts when an actionable remediation exists.

The initial image contained:

    15 blocking findings

After dependency and OS remediation:

    0 blocking findings

A clean scanner result is not treated as sufficient proof of readiness.

Regression tests and runtime validation follow the remediation.

## Use a Numeric Non-Root Identity

The first container used a dedicated named user:

    appuser

Local Docker validation confirmed that the process was not running as root.

However, Kubernetes later reported:

    runAsNonRoot and image has non-numeric user (appuser)

The issue was not that the process required root.

The issue was that Kubernetes could not deterministically verify the named image user.

The Dockerfile was changed to:

    USER 10001:10001

This preserved the non-root model while making the identity verifiable by Kubernetes.

## Right-Size the Workload Instead of Adding Infrastructure

The initial GitOps rollout encountered insufficient schedulable CPU requests on the shared AKS node.

The node's actual CPU usage was not the main issue.

Kubernetes scheduling was constrained by already reserved CPU requests.

I evaluated adding a dedicated user node pool.

That approach was blocked by the available Sweden Central vCPU quota.

For this small validation workload, increasing infrastructure solely to avoid changing the application's request was not justified.

The application CPU request was reduced in controlled steps.

Final request:

    cpu: 5m

The application still retains:

    cpu limit: 250m

This is an environment-specific validation setting and not a general production sizing recommendation.

## Use Lightweight Prometheus and Grafana

The shared AKS node was already request constrained.

Deploying a larger monitoring bundle would consume capacity that was not necessary for the objectives of this project.

I therefore used lightweight standalone Prometheus and Grafana components.

The monitoring stack focuses on the runtime signals needed for the application:

- request rate
- request latency
- order counters
- target health
- Kubernetes resource behavior

## Keep Build-Time and Runtime Visibility Separate

I did not attempt to copy all CI, SonarQube, or ACR information into Grafana.

Build-time visibility belongs primarily in:

    Azure DevOps
    SonarQube
    Trivy
    ACR

Runtime visibility belongs primarily in:

    Prometheus
    Grafana
    Kubernetes metrics
    application logs
    HPA state

This keeps the runtime dashboard operationally useful.

## Run k6 Inside the Private Environment

The application is not publicly exposed for load testing.

Instead of weakening the network model to generate traffic from the developer laptop, k6 runs inside Kubernetes.

This gives the load generator direct access to the private service and keeps the test consistent with the runtime architecture.

## Tune HPA for the Validation Environment

The initial HPA CPU target was:

    50%

During the first controlled load test, application CPU remained around:

    40%

Kubernetes correctly kept the application at one replica because utilization was below the configured target.

I did not classify that as an HPA failure.

For the explicit autoscaling validation, the target was changed to:

    30%

The same controlled workload then caused scale-out.

The application reached:

    3 replicas

which is the configured maximum.

The lower threshold is intentional for this small shared environment.

## Limit HPA Maximum Replicas

The HPA maximum is:

    3

The objective is to prove scale-out behavior without allowing a portfolio workload to consume unnecessary shared AKS capacity.

The value is appropriate for this environment but is not intended as a universal production recommendation.

## Temporary Elevated Access Must Be Revoked

Some bootstrap operations required permissions beyond the normal validation identity.

Where elevated AKS RBAC was required, it was used for the specific controlled operation.

After validation, the elevated assignment was removed.

The normal identity returned to:

    Azure Kubernetes Service Cluster User Role
    Azure Kubernetes Service RBAC Reader

The repository keeps evidence of privilege revocation.

## Do Not Broaden Reader Access Just for Screenshots

The Reader identity could inspect the runtime state required by the validation pipelines.

It could not perform operations such as arbitrary port forwarding or unrestricted execution inside pods.

When Grafana evidence became difficult to retrieve, I did not grant additional Kubernetes privileges merely for screenshot convenience.

Instead, I used an in-cluster evidence workflow compatible with the private architecture.

## Do Not Expose Grafana for Portfolio Evidence

Grafana was reachable inside Kubernetes but not directly from the developer laptop.

The private agent VM also could not route directly to the Kubernetes service CIDR.

Possible shortcuts included:

- public LoadBalancer
- public ingress
- broader Kubernetes privileges
- additional Bastion infrastructure

I did not use those options.

A temporary in-cluster capture workload rendered the dashboard.

The PNG was retrieved through Azure DevOps and stored as repository evidence.

The temporary capture resources were removed afterward.

This preserved the intended private runtime model.

## Keep Real Failure Evidence

I retained evidence from failures that materially affected the design.

Examples include:

- Python runtime compatibility
- Docker Desktop engine failure
- vulnerability remediation
- AKS scheduling pressure
- regional vCPU quota
- missing ACR artifact
- non-numeric container identity
- HPA threshold behavior
- private Grafana evidence retrieval

I did not intentionally recreate failures after they were fixed.

The repository documents them because they explain why the final implementation looks the way it does.

## Cost Is an Engineering Constraint

The project reuses existing private Azure infrastructure.

I avoided creating another AKS cluster for the portfolio workload.

I also avoided adding infrastructure solely to make evidence collection easier.

Monitoring is deliberately lightweight.

HPA is capped.

Temporary evidence workloads are removed after use.

These choices keep the platform technically meaningful without spending Azure credits on resources that do not improve the engineering outcome.
