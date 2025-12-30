import sys
import os

# Add parent directory to path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from mangum import Mangum

# Mangum adapter for AWS Lambda/Vercel compatibility
handler = Mangum(app, lifespan="off")
