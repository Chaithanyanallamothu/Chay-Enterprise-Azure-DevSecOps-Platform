# 12 - Incident and Recovery Validation

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Objective

Several useful engineering decisions in this project came from real failures encountered while implementing the platform.

I retained those incidents because they demonstrate diagnosis and recovery rather than showing only successful pipeline screenshots.

The failures were not intentionally recreated after remediation.

## Incident 1 - Python Runtime Compatibility

### Symptom

Local dependency installation failed while using:

    Python 3.14.7

The failure involved `pydantic-core` and PyO3 compatibility.

### Diagnosis

The issue was isolated to the local Python/toolchain combination rather than application business logic.

### Recovery

Development was standardized on:

    Python 3.12.14

The virtual environment was recreated and the test baseline passed.

### Outcome

Local development and the container runtime now use the same Python major/minor baseline.

---

## Incident 2 - Docker Desktop Engine Failure

### Symptom

Docker Desktop encountered a containerd metadata error containing:

    read-only file system

Docker API calls subsequently returned HTTP 500 responses.

### Diagnosis

Docker context and daemon checks separated the failure from the application Dockerfile.

### Recovery

Docker Desktop was restarted.

After restart:

- Docker server communication recovered
- `docker info` succeeded
- `hello-world` succeeded
- the application image built again

### Outcome

A factory reset was avoided because it was not required.

Evidence:

    docs/evidence/screenshots/02-docker/troubleshooting/
    └── 01-docker-engine-500-error.png

---

## Incident 3 - Actionable Container Vulnerabilities

### Symptom

The initial image produced:

    Debian HIGH:       9
    Debian CRITICAL:   3
    Python HIGH:       3

    Total blocking:   15

### Diagnosis

Findings existed in both the OS package layer and Python dependency layer.

### Recovery

Python dependencies were updated and the Debian package layer was refreshed during the Docker build.

### Validation

The same blocking policy later returned:

    0 blocking HIGH/CRITICAL findings

Application regression validation also passed.

### Outcome

Security remediation became part of the artifact path rather than a documentation-only exercise.

---

## Incident 4 - AKS Scheduling Capacity

### Symptom

The first GitOps application rollout remained Pending.

### Diagnosis

The node did not show extreme actual CPU usage.

The scheduling problem was CPU requests already reserved by workloads on the shared node.

The node was close to its allocatable CPU request capacity.

### Attempted Capacity Option

A dedicated AKS user node pool was evaluated.

The operation was blocked by the available Sweden Central subscription vCPU quota.

### Recovery

The demo application's CPU request was right-sized in controlled steps.

Final request:

    cpu: 5m

CPU limit:

    cpu: 250m

### Outcome

The workload could schedule without adding unnecessary infrastructure.

This is an environment-specific sizing decision.

---

## Incident 5 - Missing Immutable ACR Artifact

### Symptom

During GitOps rollout, the desired image could not be pulled.

Initial errors could have been interpreted as an ACR authentication problem.

### Investigation

The AKS kubelet identity and `AcrPull` assignment were checked.

The exact immutable artifact was then queried from the private ACR path.

The requested older tag was no longer present.

### Root Cause

The desired state referenced an immutable image tag that no longer existed in the registry.

The problem was therefore not simply missing kubelet registry authorization.

### Recovery

A verified production artifact was rebuilt and published through the normal CI path.

Git desired state was updated to the valid immutable image.

Final artifact:

    cce36ef47e07d29ce3e2641a0e7c0e15514da777

Digest:

    sha256:219ae166d3dccccd3c39d1212a18aec99bf6ef18bdc52340aa184d2bc6093f5da

### Outcome

The incident reinforced the importance of checking exact immutable artifact existence during GitOps troubleshooting.

---

## Incident 6 - Kubernetes Non-Root Identity

### Symptom

After the artifact issue was corrected, Kubernetes reported:

    runAsNonRoot and image has non-numeric user (appuser)

### Diagnosis

The container was already designed to run as a dedicated non-root user.

However, Kubernetes could not deterministically verify the named image user under `runAsNonRoot`.

### Recovery

The Dockerfile was changed to:

    USER 10001:10001

The corrected image passed:

- local identity validation
- Azure DevOps CI
- Trivy validation
- ACR publication
- GitOps reconciliation
- AKS runtime validation

### Outcome

The final container keeps the non-root model while using a Kubernetes-verifiable numeric identity.

---

## Incident 7 - HPA Did Not Scale at 50%

### Symptom

The first HPA load validation did not produce the expected scale-out.

### Investigation

The HPA target was:

    50%

Observed sustained application CPU was approximately:

    40%

### Diagnosis

Kubernetes was behaving correctly.

CPU utilization had not exceeded the configured target.

### Recovery

For the controlled validation environment, the target was changed to:

    30%

### Validation

Under the same deliberate load pattern, the application scaled from:

    1 -> 3 replicas

### Outcome

The threshold was tuned to observed workload behavior rather than labeling correct HPA behavior as a platform failure.

---

## Incident 8 - Private Grafana Evidence Retrieval

### Constraint

Grafana was intentionally private.

The developer laptop could not reach the private Kubernetes service.

The private Azure DevOps VM also could not directly route to the Kubernetes service CIDR for a simple direct service request.

The steady-state Reader identity did not provide unrestricted port-forwarding capability.

### Options Rejected

I did not:

- expose Grafana publicly
- create a public LoadBalancer for screenshots
- broaden Reader access merely for evidence
- add unnecessary infrastructure solely for dashboard capture

### Recovery

A temporary in-cluster dashboard capture workload was used.

The PNG was retrieved through an Azure DevOps pipeline artifact.

The final dashboard image was stored under:

    docs/evidence/screenshots/09-monitoring/
    └── 07-grafana-runtime-dashboard.png

The temporary capture workflow was removed afterward.

### Outcome

The private architecture was preserved while still producing visual runtime evidence.

---

## Privilege Recovery

Some GitOps/HPA bootstrap operations required temporary elevated access.

After the required configuration was applied, the elevated assignment was revoked.

The private-agent steady-state access returned to:

    Azure Kubernetes Service Cluster User Role
    Azure Kubernetes Service RBAC Reader

Evidence:

    docs/evidence/screenshots/12-incident-recovery/
    ├── 01-gitops-recovery-running.png
    └── 02-temporary-cluster-admin-revoked.png

Additional HPA privilege-revocation evidence:

    docs/evidence/screenshots/11-autoscaling/
    └── 01-hpa-temporary-admin-revoked.png

## Recovery Pattern

Across the incidents, the working pattern was:

    Observe symptom
        |
        v
    Separate platform layer from application layer
        |
        v
    Verify the assumption
        |
        v
    Apply the smallest justified change
        |
        v
    Re-run validation
        |
        v
    Remove temporary access/workarounds
        |
        v
    Preserve evidence

## Final State

The recovered platform now has:

- Python 3.12 development baseline
- working local Docker runtime
- zero blocking fixable HIGH/CRITICAL findings under the implemented Trivy policy
- schedulable application resources
- verified immutable ACR artifact
- numeric non-root container identity
- healthy GitOps-managed workload
- private Prometheus/Grafana monitoring
- successful in-cluster k6 baseline
- validated HPA scale-out
- steady-state least-privilege AKS validation access

The incident history is retained because it explains the final engineering decisions rather than presenting the platform as if every assumption was correct on the first attempt.
