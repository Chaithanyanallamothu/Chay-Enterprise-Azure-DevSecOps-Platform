# Incident Recovery Guide

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Purpose

This is the operational reference for failure patterns encountered while building and validating the platform.

The detailed historical record is maintained in:

    docs/evidence/12-incident-recovery.md

## Python Compatibility

Historical condition:

    Python 3.14.7
        |
        v
    pydantic-core / PyO3 compatibility failure

Validated recovery:

    Python 3.12.14

The project development baseline is Python 3.12.

## Docker Engine Failure

Historical symptoms:

    read-only file system
    Docker API HTTP 500

Recovery:

    Verify Docker context
        |
        v
    Verify daemon
        |
        v
    Restart Docker Desktop
        |
        v
    Validate docker info
        |
        v
    Validate hello-world
        |
        v
    Rebuild application

A factory reset was not required.

## Security Gate Failure

Determine whether the blocking finding exists in:

- Python dependencies
- OS packages
- final production image

The implemented Trivy policy blocks actionable fixable HIGH and CRITICAL findings.

After remediation:

1. rerun the same security policy
2. rebuild the production image
3. rerun functional validation
4. publish only after the artifact passes

A successful scanner result alone is not application validation.

## Pod Remains Pending

Inspect Kubernetes scheduler events first.

Compare actual CPU utilization with CPU requests already reserved.

A node can have low actual CPU usage while still having insufficient schedulable request capacity.

Check:

- requested CPU and memory
- allocatable resources
- existing workload reservations
- replica count
- regional/subscription quota

During this project, an additional node pool was evaluated but available Sweden Central vCPU quota prevented that option.

The demo workload was right-sized for the existing environment instead.

## Image Pull Failure

Do not immediately assume registry authorization is the root cause.

Validate:

    AKS kubelet identity
        |
        v
    AcrPull assignment
        |
        v
    Exact immutable tag in ACR
        |
        v
    Helm desired-state image tag

A real project incident occurred because the desired immutable artifact was no longer present in ACR.

## Kubernetes Non-Root Failure

Historical error:

    runAsNonRoot and image has non-numeric user (appuser)

Validated recovery:

    USER 10001:10001

Do not disable `runAsNonRoot` or change the application to root as a shortcut.

## Argo CD Reconciliation

Validate:

- repository revision
- Helm path
- immutable image tag
- namespace
- Argo CD project permissions
- synchronization state

When introducing a new Kubernetes resource type, confirm that the Argo CD project permits it.

The HPA required an explicit project authorization change.

Do not replace normal GitOps reconciliation with direct CI deployment.

## HPA Does Not Scale

Compare observed CPU utilization with the configured target.

Historical observation:

    target:       50%
    observed CPU: approximately 40%
    result:       no scale-out

This was correct HPA behavior.

For the controlled validation environment, the target was changed to:

    30%

The workload subsequently scaled:

    1 -> 2 -> 3 replicas

## Prometheus Shows Zero Request Rate

Check whether requests occurred inside the query window.

A cumulative request counter can contain substantial historical traffic while:

    rate(...[5m]) = 0

when no requests occurred during the last five minutes.

This is not automatically a Prometheus failure.

## P95 or P99 Is Empty

Latency quantiles can be empty or NaN when the selected window contains no histogram observations.

Validate:

    scrape target
        |
        v
    recent traffic
        |
        v
    histogram series
        |
        v
    quantile query

before changing the dashboard.

## Private Grafana Access

Grafana is private by design.

Do not expose it publicly simply for troubleshooting or screenshot collection.

The project used a temporary in-cluster capture workflow for final dashboard evidence and removed that workflow afterward.

## Temporary Elevated AKS Access

When controlled bootstrap work requires elevated access:

    Grant
      |
      v
    Perform specific operation
      |
      v
    Validate
      |
      v
    Revoke
      |
      v
    Verify steady-state access

The normal private-agent model remains Reader-oriented.

## Incident Information

For an operational escalation, capture:

- affected component
- Git commit SHA
- image tag and digest when relevant
- Azure DevOps pipeline run
- namespace
- deployment/pod state
- Kubernetes events
- relevant logs
- HPA state when relevant
- Prometheus target/query state when relevant
- actions already attempted

Never include credentials, tokens, private keys, registry credentials, or service-connection secrets.

## Detailed Incident History

The detailed evidence record covers the real implementation incidents involving:

- Python compatibility
- Docker Desktop
- vulnerability remediation
- AKS scheduling capacity
- missing immutable ACR artifact
- Kubernetes non-root identity
- HPA threshold behavior
- private Grafana evidence retrieval
- temporary privilege revocation

See:

    docs/evidence/12-incident-recovery.md
