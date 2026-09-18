# 02 - Container Build and Runtime Validation

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Objective

The container checkpoint validated that the FastAPI application could run consistently as a hardened non-root OCI container before becoming the artifact consumed by the CI/CD platform.

## Base Image

The application uses:

    python:3.12-slim

The Dockerfile configures:

    PYTHONDONTWRITEBYTECODE=1
    PYTHONUNBUFFERED=1

The application listens on:

    8080

## Non-Root Runtime

The original image created a dedicated named user:

    appuser

Local Docker validation confirmed that the process did not run as root.

That configuration was valid from the local container-runtime perspective, but a later AKS rollout exposed an important Kubernetes compatibility issue.

Kubernetes reported:

    runAsNonRoot and image has non-numeric user (appuser)

The problem was not that the application required root privileges.

Kubernetes could not deterministically verify that the named image user was non-root while enforcing `runAsNonRoot`.

The final Dockerfile therefore uses:

    USER 10001:10001

Final identity:

    UID 10001
    GID 10001

This preserves the non-root security model while making the identity unambiguous to Kubernetes.

## Runtime Validation

The final container was validated for:

- successful image build
- Linux/amd64 target architecture
- numeric non-root identity
- application startup
- health endpoint
- readiness endpoint
- version endpoint
- application behavior
- Prometheus metrics

The explicit identity check confirmed:

    uid=10001(appuser)
    gid=10001(appgroup)

The image therefore retains a readable Linux user/group mapping while declaring the runtime numerically.

## Docker Desktop Incident

During the container workflow, Docker Desktop itself failed locally.

The initial error involved containerd metadata storage and included:

    read-only file system

Subsequent Docker API calls returned HTTP 500 errors.

I separated the daemon problem from the Dockerfile/application by checking the Docker context and engine state.

Docker Desktop was restarted.

After restart:

- Docker client/server communication recovered
- `docker info` worked
- the `desktop-linux` context responded
- `hello-world` executed
- the application image built successfully

A factory reset was not required.

This incident was retained because it demonstrates the distinction between application/container failures and local container-engine failures.

## Security Remediation Regression

The container was also rebuilt after dependency and Debian package remediation.

The remediated image was revalidated instead of assuming that a clean vulnerability result meant the application still behaved correctly.

The runtime continued to pass application endpoint validation.

## Final Kubernetes-Compatible Container

The final GitOps-compatible image is based on the numeric non-root Dockerfile.

The corrected artifact was later built by Azure DevOps and published to private ACR using the full Git SHA:

    cce36ef47e07d29ce3e2641a0e7c0e15514da777

The final registry digest is:

    sha256:219ae166d3dccccd3c39d1212a18aec99bf6ef18bdc52340aa184d2bc6093f5da

## Evidence

Primary screenshots:

    docs/evidence/screenshots/02-docker/
    ├── 01-docker-image-build-and-metadata.png
    ├── 02-container-runtime-validation.png
    ├── 03-remediated-container-runtime-validation.png
    └── troubleshooting/
        └── 01-docker-engine-500-error.png

The earlier named-user evidence is retained as implementation history.

The final platform state is the numeric UID/GID `10001:10001` configuration.
