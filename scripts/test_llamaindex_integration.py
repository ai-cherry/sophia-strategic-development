#!/usr/bin/env python
"""
Test script for LlamaIndex integration in Sophia AI.

This script demonstrates how to use the LlamaIndex integration for document
processing and querying. It processes a sample document and performs a query.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

# Import secret management
from infrastructure.esc.llamaindex_secrets import setup_llamaindex_secrets

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import the LlamaIndex processor
from backend.integrations.llamaindex_integration import LlamaIndexProcessor

# Sample document for testing
SAMPLE_DOCUMENT = """
# Pay Ready Apartment Lease Agreement

## LEASE AGREEMENT

THIS LEASE AGREEMENT (hereinafter referred to as the "Agreement") made and entered into this 1st day of June, 2025, by and between PAY READY PROPERTIES LLC (hereinafter referred to as "Landlord") and JOHN DOE (hereinafter referred to as "Tenant").

WITNESSETH:

WHEREAS, Landlord is the fee owner of certain real property being, lying and situated in Los Angeles County, California, such real property having a street address of 123 Main Street, Apartment 4B, Los Angeles, CA 90001 (hereinafter referred to as the "Premises").

WHEREAS, Landlord desires to lease the Premises to Tenant upon the terms and conditions as contained herein; and

WHEREAS, Tenant desires to lease the Premises from Landlord on the terms and conditions as contained herein;

NOW, THEREFORE, for and in consideration of the covenants and obligations contained herein and other good and valuable consideration, the receipt and sufficiency of which is hereby acknowledged, the parties hereto agree as follows:

1. TERM. Landlord leases to Tenant and Tenant leases from Landlord the above described Premises together with any and all appurtenances thereto, for a term of twelve (12) months, such term beginning on June 1, 2025, and ending at 12 midnight on May 31, 2026.

2. RENT. The total rent for the term hereof is the sum of TWENTY-FOUR THOUSAND DOLLARS ($24,000.00) payable on the 1st day of each month of the term, in equal installments of TWO THOUSAND DOLLARS ($2,000.00). All such payments shall be made to Landlord at Landlord's address as set forth in the preamble to this Agreement on or before the due date and without demand.

3. DAMAGE DEPOSIT. Upon the due execution of this Agreement, Tenant shall deposit with Landlord the sum of TWO THOUSAND DOLLARS ($2,000.00) receipt of which is hereby acknowledged by Landlord, as security for any damage caused to the Premises during the term hereof. Such deposit shall be returned to Tenant, without interest, and less any set off for damages to the Premises upon the termination of this Agreement.

4. USE OF PREMISES. The Premises shall be used and occupied by Tenant and Tenant's immediate family, consisting of JOHN DOE, JANE DOE, and JIMMY DOE, exclusively, as a private single-family dwelling, and no part of the Premises shall be used at any time during the term of this Agreement by Tenant for the purpose of carrying on any business, profession, or trade of any kind, or for any purpose other than as a private single-family dwelling.
"""

# Sample queries for testing
SAMPLE_QUERIES = [
    "What is the monthly rent amount?",
    "How long is the lease term?",
    "What is the damage deposit amount?",
    "Who are the tenants listed in the agreement?",
    "What is the address of the property?"
]

async def process_document():
    """Process the sample document with LlamaIndex."""
    logger.info("Initializing LlamaIndex processor")
    processor = LlamaIndexProcessor()
    
    logger.info("Processing sample document")
    result = await processor.process_document(
        document=SAMPLE_DOCUMENT,
        context={"test": True}
    )
    
    logger.info(f"Document processing result: {result}")
    return result

async def query_document():
    """Query the processed document with sample queries."""
    logger.info("Initializing LlamaIndex processor")
    processor = LlamaIndexProcessor()
    
    logger.info("Running sample queries")
    for query in SAMPLE_QUERIES:
        logger.info(f"Query: {query}")
        results = []
        async for result in processor.query_documents(
            query=query,
            context={"test": True}
        ):
            results.append(result)
            logger.info(f"Result: {result}")
        
        logger.info(f"Found {len(results)} results for query: {query}")
    
    return True

async def run_tests():
    """Run all tests."""
    logger.info("Starting LlamaIndex integration tests")
    
    # Process document
    process_result = await process_document()
    if process_result.get("status") != "success":
        logger.error("Document processing failed")
        return False
    
    # Query document
    query_result = await query_document()
    if not query_result:
        logger.error("Document querying failed")
        return False
    
    logger.info("All tests completed successfully")
    return True

if __name__ == "__main__":
    logger.info("Running LlamaIndex integration test script")
    
    # Setup LlamaIndex secrets from Pulumi ESC
    logger.info("Setting up LlamaIndex secrets from Pulumi ESC")
    setup_llamaindex_secrets()
    
    # Run the tests
    result = asyncio.run(run_tests())
    
    # Exit with appropriate status code
    sys.exit(0 if result else 1)
