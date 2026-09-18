# 05 - Security Scanning and Remediation

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Objective

Security scanning is integrated into the delivery workflow so actionable vulnerabilities are addressed before the production container is published.

Trivy is used for both dependency/source-oriented validation and final container validation.

## Blocking Policy

The implemented blocking policy focuses on fixable:

    HIGH
    CRITICAL

findings.

Unfixed vulnerabilities are excluded from this particular automated blocking policy.

The purpose is to fail CI for actionable HIGH/CRITICAL findings for which a remediation is available.

## Initial Findings

The initial image contained blocking findings in both the Debian OS layer and Python dependency layer.

Initial result:

    Debian HIGH:       9
    Debian CRITICAL:   3
    Python HIGH:       3

    Total blocking:   15

This was treated as a remediation requirement rather than accepting the initial container as the production baseline.

## Python Dependency Remediation

The application dependency set was updated to patched versions.

The final application requirements include:

    fastapi==0.141.1
    starlette==1.3.1
    uvicorn[standard]==0.35.0
    prometheus-client==0.22.1
    pydantic==2.11.7

Development dependencies include:

    pytest==8.4.1
    httpx==0.28.1
    pytest-cov==6.2.1
    ruff==0.12.10

## OS-Layer Remediation

The Docker build also updates the Debian package layer before installing application dependencies.

This addressed fixable vulnerabilities inherited from the base image/package state.

## Final Security Gate

After remediation, Trivy was executed with the same HIGH/CRITICAL blocking policy.

Final result:

    Debian HIGH/CRITICAL: 0
    Python HIGH/CRITICAL: 0

    Total blocking:       0

The gate returned a successful exit status.

## Regression After Security Changes

I did not treat the scanner result as proof that the application still worked.

After remediation, the application was rebuilt and runtime validation was repeated.

The remediated container continued to pass endpoint and application checks.

## CI Integration

Security scanning is integrated into Azure DevOps.

The workflow contains security validation before artifact publication and an additional scan against the exact production image built on the private agent.

The production sequence is:

    Build production image
          |
          v
    Scan exact image
          |
          v
    HIGH/CRITICAL gate
          |
          v
    Push same image to private ACR

The production artifact is not rebuilt between the final scan and publication.

## Trivy Version

The project validation used:

    Trivy 0.74.0

Pinning the tool version makes the CI behavior more reproducible than silently changing scanner versions on every run.

## Security Outcome

The important result is not simply that the final screenshot is green.

The implementation demonstrates:

    Initial actionable findings
          |
          v
    Identify affected layers
          |
          v
    Remediate dependencies and OS packages
          |
          v
    Re-run security policy
          |
          v
    0 blocking findings
          |
          v
    Re-run functional validation

## Evidence

Screenshots under:

    docs/evidence/screenshots/05-security/

capture:

- initial dependency/security remediation work
- remediation validation
- remediated image gate
- Azure DevOps security stage
- CI security gates

The initial findings are retained because they explain the remediation rather than presenting only the final clean scan.
