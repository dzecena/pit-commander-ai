"""
Lambda handler for FastAPI application
"""

from mangum import Mangum
from .main import app

# Create the Lambda handler
lambda_handler = Mangum(app, lifespan="off")