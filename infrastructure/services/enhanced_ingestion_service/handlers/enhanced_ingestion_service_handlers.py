"""
EnhancedIngestionService Handlers
Request/response handlers and API endpoints
"""

from core.optimized_connection_manager import connection_manager
from core.performance_monitor import performance_monitor
import asyncio
import io
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4
from pydantic import BaseModel
    import pandas as pd
    from docx import Document as DocxDocument
    import PyPDF2
    import openpyxl
    import pptx
        import re

from .models.enhanced_ingestion_service_models import *

# Handlers extracted from main file
# TODO: Extract actual handler classes from source
