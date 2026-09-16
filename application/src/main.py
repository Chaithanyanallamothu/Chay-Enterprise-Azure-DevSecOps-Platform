import os
import random
import time
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

APP_NAME = "chay-demo-api"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

app = FastAPI(
    title="Chay DevSecOps Demo API",
    version=APP_VERSION,
)

REQUEST_COUNT = Counter(
    "chay_http_requests_total",
    "Total HTTP requests handled by the application",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "chay_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)

ORDERS_CREATED = Counter(
    "chay_orders_created_total",
    "Total successfully created orders",
)

ORDERS_FAILED = Counter(
    "chay_orders_failed_total",
    "Total failed order requests",
)


class OrderRequest(BaseModel):
    product_id: str = Field(min_length=1, max_length=50)
    quantity: int = Field(gt=0, le=100)
    mode: Literal["normal", "slow", "fail"] = "normal"


@app.get("/")
def root():
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.get("/version")
def version():
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
    }


@app.get("/api/orders")
def order_statistics():
    return {
        "service": APP_NAME,
        "message": "Order service is available",
    }


@app.post("/api/orders", status_code=201)
def create_order(order: OrderRequest):
    start = time.perf_counter()

    try:
        if order.mode == "slow":
            time.sleep(random.uniform(0.5, 1.5))

        if order.mode == "fail":
            ORDERS_FAILED.inc()
            REQUEST_COUNT.labels(
                method="POST",
                endpoint="/api/orders",
                status="500",
            ).inc()

            raise HTTPException(
                status_code=500,
                detail="Simulated order processing failure",
            )

        ORDERS_CREATED.inc()

        REQUEST_COUNT.labels(
            method="POST",
            endpoint="/api/orders",
            status="201",
        ).inc()

        return {
            "status": "created",
            "product_id": order.product_id,
            "quantity": order.quantity,
            "version": APP_VERSION,
        }

    finally:
        REQUEST_LATENCY.labels(
            method="POST",
            endpoint="/api/orders",
        ).observe(time.perf_counter() - start)


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
