"""
EnhancedIngestionService Utilities
Helper functions and utility classes
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

# Utilities extracted from main file
# TODO: Extract actual utility functions from source
