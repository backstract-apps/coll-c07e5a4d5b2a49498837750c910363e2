from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from database import engine

from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
import models
import uvicorn
from routes import router

import time
import logging_loki
from multiprocessing import Queue
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # Re-add this import
import logging
import sys
import os
from telemetry_config import setup_telemetry_and_logging

setup_telemetry_and_logging()


# Database setup
models.Base.metadata.create_all(bind=engine)

# Prometheus core metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency',
                            ['method', 'endpoint', 'http_status'])
IN_PROGRESS = Gauge('http_requests_in_progress', 'HTTP requests in progress')

app = FastAPI(title='Mayson Generated APIs - coll-c07e5a4d5b2a49498837750c910363e2', debug=False,
              docs_url='/jolly-aditya-815944ac9c4111f09b274e585a3d7fc927/docs',
              openapi_url='/jolly-aditya-815944ac9c4111f09b274e585a3d7fc927/openapi.json',
              root_path='')


FastAPIInstrumentor.instrument_app(app)  # Re-add this line



# Global Exception Handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    import traceback
    status_code = getattr(exc, 'status_code', 500) or getattr(exc, 'code', 500)
    
    # Log detailed error information
    logger.error(f"Exception in {request.method} {request.url.path}: {str(exc)}")
    logger.error(f"Exception type: {type(exc).__name__}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Check for specific error types and provide better messages
    error_message = str(exc)
    if "Expecting value: line 1 column 1" in error_message:
        error_message = "Failed to parse platform API response - resource may not exist or endpoint unavailable"
    elif "404" in error_message or "Not Found" in error_message:
        error_message = "Resource not found on platform - check resource configuration and permissions"
    
    return JSONResponse(
        status_code=500,
        content={
            "status": f"{status_code}",
            "message": f"Global exception caught: {error_message}"
        }
    )

@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": f"{exc.status_code}",
            "message": f"{exc.detail}"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    status_code = getattr(exc, 'status_code', 500) or getattr(exc, 'code', 500)
    return JSONResponse(
        status_code=500,
        content={
            "status": f"{status_code}",
            "message": f"{str(exc)}"
        }
    )



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    router,
    prefix='/jolly-aditya-815944ac9c4111f09b274e585a3d7fc927/api',
    tags=['APIs v1']
)


# Middleware for Prometheus metrics
@app.middleware('http')
async def prometheus_middleware(request: Request, call_next):
    method = request.method
    path = request.url.path
    start_time = time.time()
    status_code=None

    IN_PROGRESS.inc()  # Increment in-progress requests

    # Log incoming request details for file uploads
    if "file-upload" in path:
        logger.info(f"Incoming file upload request: {method} {path}")
        logger.info(f"Query params: {dict(request.query_params)}")
        logger.info(f"Headers: {dict(request.headers)}")

    try:
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time()-start_time)*1000
        if "/metrics" not in request.url.path and "/loki" not in request.url.path:
            status_code = response.status_code
            emoji = "➡️"
            if 200 <= status_code < 300:
                emoji += " ✅"  # Success
                log_level = logger.info
            elif 300 <= status_code < 400:
                emoji += " ↪️"  # Redirection
                log_level = logger.info
            elif 400 <= status_code < 500:
                emoji += " ⚠️"  # Client Error
                log_level = logger.warning
            else:  # 500 and above
                emoji += " ❌"  # Server Error
                log_level = logger.error

            log_level(
                f"{emoji} {request.method} {request.url.path} Status: {status_code} response:{response} ⏱️ Time: {process_time:.2f}ms"
            )
            
            # For errors, try to log response body if available
            if status_code >= 400 and hasattr(response, 'body'):
                try:
                    response_body = getattr(response, 'body', None)
                    if response_body:
                        logger.error(f"Error response body: {response_body[:500]}")
                except:
                    pass
    except Exception as e:
        status_code = 500  # Internal server error
        raise e
    finally:
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=path, http_status=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=path, http_status=status_code).observe(duration)
        IN_PROGRESS.dec()  # Decrement in-progress requests

    return response


# Prometheus' metrics endpoint
prometheus_app = make_asgi_app()
app.mount('/metrics', prometheus_app)

def main():
    uvicorn.run('main:app', host='127.0.0.1', port=7070, reload=True)


if __name__ == '__main__':
    main()