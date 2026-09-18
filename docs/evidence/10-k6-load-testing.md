# 10 - k6 Baseline Load Testing

**Author:** Chaithanya Nallamothu
**Role:** Senior DevSecOps Engineer

## Objective

The baseline load test validates application behavior under controlled concurrent traffic inside the private AKS environment.

The purpose is not to claim production-scale performance.

It establishes a repeatable runtime baseline and proves that load generation can occur without exposing the private application publicly.

## Test Location

The developer laptop cannot directly access the private Kubernetes service.

k6 therefore runs inside Kubernetes.

This preserves the private network model.

## Test Definition

Baseline test:

    load-tests/baseline.js

Configuration:

    Virtual users: 5
    Duration:      60 seconds

The scenario exercises:

    GET /health
    GET /api/orders

## Thresholds

The baseline includes thresholds for:

    failed requests < 1%
    P95 latency < 1000 ms
    checks > 99%

## Validated Result

Successful validation produced:

    Iterations:          595
    HTTP requests:       1,190
    Checks passed:       100%
    Failed requests:     0.00%
    P95 latency:         approximately 3.88 ms
    Request throughput:  approximately 19.8 req/s

The test completed successfully.

## Security Context

The k6 validation workload was configured as a controlled Kubernetes workload rather than requiring public application exposure.

This kept load testing consistent with the private platform design.

## Interpretation

The result demonstrates that the demo API remained healthy under the defined baseline scenario.

It should not be interpreted as a capacity benchmark for a production system because:

- the workload is intentionally small
- the test duration is short
- the AKS environment is shared
- the scenario is designed for platform validation rather than production sizing

## Relationship to Autoscaling Test

The baseline test and HPA test are intentionally separate.

Baseline:

    5 VUs / 60s
    validate normal behavior

Autoscaling:

    40 VUs / 3m
    create sustained CPU pressure

Separating the scenarios keeps normal runtime validation distinct from deliberate scale-out validation.

## Evidence

Screenshot:

    docs/evidence/screenshots/10-load-testing/
    └── 01-k6-private-aks-baseline-passed.png

The screenshot captures the successful private-AKS k6 baseline rather than a locally simulated result.
