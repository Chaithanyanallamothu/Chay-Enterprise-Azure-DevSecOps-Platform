# 04 - SonarQube Cloud Quality Gate

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Objective

SonarQube Cloud provides source-quality and security analysis within the Azure DevOps application-validation stage.

The objective is to make quality evaluation part of CI rather than treating the Sonar dashboard as a separate manual review.

## Integration

Azure DevOps uses the configured SonarQube Cloud service connection:

    chay-sonarqube-cloud

The pipeline uses CLI scanner mode with file-based project configuration.

The project configuration is maintained in:

    sonar-project.properties

This keeps the analysis settings version controlled.

## Project

SonarQube Cloud project:

    Chay-Enterprise-Azure-DevSecOps-Platform

The analysis is driven by Azure DevOps rather than Sonar automatic analysis.

## Validated Quality State

The validated project state showed:

    Quality Gate:       Passed
    Coverage:           approximately 94.1%
    Security rating:    A
    Security issues:    0
    Duplication:        0.0%

The repository retains both Azure DevOps and Sonar dashboard evidence.

## Explicit CI Enforcement

The initial integration prepared, analyzed, and published the Sonar Quality Gate result.

During the final platform review, I made the CI enforcement behavior explicit by adding:

    sonar.qualitygate.wait=true

This instructs the scanner to wait for the Quality Gate result and makes an unsuccessful Quality Gate fail the analysis execution.

The change was committed as:

    5baf04a
    Enforce SonarQube quality gate in CI

## Final Validation

The enforcement configuration was validated through Azure DevOps run:

    #20260918.28

The pipeline completed successfully.

The summary showed:

    100% tests passed
    94.12% coverage

and all three main pipeline stages completed successfully.

I did not intentionally introduce a failing Quality Gate simply to manufacture failure evidence.

The repository contains the enforcement configuration and the successful CI execution using that configuration.

## Separation from Runtime Observability

SonarQube is treated as build-time quality visibility.

It is not copied into Grafana simply to create a single dashboard.

The platform separates:

    Build-time:
      Azure DevOps
      SonarQube
      Trivy
      ACR artifact metadata

    Runtime:
      Prometheus
      Grafana
      Kubernetes metrics
      HPA state
      application logs

## Evidence

Screenshots:

    docs/evidence/screenshots/04-sonarqube/
    ├── 01-sonarqube-azure-devops-service-connection.png
    ├── 02-azure-devops-sonarqube-quality-gate-passed.png
    ├── 03-sonarqube-quality-gate-dashboard.png
    └── 04-enforced-quality-gate-ci-passed.png

The fourth screenshot represents the final CI run after explicit Quality Gate enforcement was committed.
