#!/usr/bin/env python3
"""
CoStar Data Ingestion Script for Sophia AI

Standalone script for processing CoStar real estate market data files
Supports batch processing, validation, and database import operations
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import List

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.mcp.costar_mcp_server import CoStarMCPServer, CoStarImportResult


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("costar_ingestion.log"),
        ],
    )


async def process_single_file(
    server: CoStarMCPServer, file_path: Path
) -> CoStarImportResult:
    """
    Process a single CoStar data file."""
    logger = logging.getLogger(__name__)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() not in [".csv", ".xlsx", ".xls"]:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    logger.info(f"Processing file: {file_path}")

    try:
        result = await server.process_file(file_path)

        # Log results
        if result.import_status == "success":
            logger.info(
                f"✅ Successfully imported {result.records_imported} records from {file_path.name}"
            )
        elif result.import_status == "partial":
            logger.warning(
                f"⚠️  Partially imported {result.records_imported}/{result.records_processed} records from {file_path.name}"
            )
            logger.warning(f"   Failed records: {result.records_failed}")
        else:
            logger.error(f"❌ Failed to import data from {file_path.name}")
            if result.error_message:
                logger.error(f"   Error: {result.error_message}")

        logger.info(f"   Processing time: {result.processing_time_seconds:.2f} seconds")

        return result

    except Exception as e:
        logger.error(f"❌ Error processing {file_path.name}: {e}")
        raise


async def process_directory(
    server: CoStarMCPServer, directory_path: Path, recursive: bool = False
) -> List[CoStarImportResult]:
    """Process all CoStar data files in a directory."""
    logger = logging.getLogger(__name__)

    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    if not directory_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory_path}")

    # Find all supported files
    patterns = ["*.csv", "*.xlsx", "*.xls"]
    files = []

    for pattern in patterns:
        if recursive:
            files.extend(directory_path.rglob(pattern))
        else:
            files.extend(directory_path.glob(pattern))

    if not files:
        logger.warning(f"No CoStar data files found in {directory_path}")
        return []

    logger.info(f"Found {len(files)} files to process")

    results = []
    for file_path in sorted(files):
        try:
            result = await process_single_file(server, file_path)
            results.append(result)
        except Exception as e:
            logger.error(f"Skipping file {file_path.name} due to error: {e}")
            continue

    return results


async def validate_file(file_path: Path) -> dict:
    """Validate a CoStar data file without importing."""
    logging.getLogger(__name__)

    validation_result = {
        "file_path": str(file_path),
        "valid": False,
        "errors": [],
        "warnings": [],
        "record_count": 0,
        "columns": [],
    }

    try:
        import pandas as pd

        # Read file
        if file_path.suffix.lower() == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        validation_result["record_count"] = len(df)
        validation_result["columns"] = list(df.columns)

        # Check for required columns
        required_columns = ["metro_area", "market_date"]
        missing_required = []

        for req_col in required_columns:
            # Check for exact match or aliases
            column_found = False
            for col in df.columns:
                if col.lower().replace(" ", "_") in [
                    req_col,
                    "market",
                    "metro",
                    "date",
                    "period",
                ]:
                    column_found = True
                    break

            if not column_found:
                missing_required.append(req_col)

        if missing_required:
            validation_result["errors"].append(
                f"Missing required columns: {', '.join(missing_required)}"
            )

        # Check data quality
        if len(df) == 0:
            validation_result["errors"].append("File contains no data rows")
        elif len(df) > 100000:
            validation_result["warnings"].append(
                f"Large file with {len(df)} records - processing may take time"
            )

        # Check for empty critical columns
        for col in df.columns:
            if col.lower().replace(" ", "_") in ["metro_area", "market"]:
                empty_count = df[col].isna().sum()
                if empty_count > 0:
                    validation_result["warnings"].append(
                        f"Column '{col}' has {empty_count} empty values"
                    )

        validation_result["valid"] = len(validation_result["errors"]) == 0

    except Exception as e:
        validation_result["errors"].append(f"Failed to read file: {str(e)}")

    return validation_result


async def main():
    """Main function for CoStar data ingestion script."""
    parser = argparse.ArgumentParser(
        description="CoStar Data Ingestion Script for Sophia AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single file
  python scripts/ingest_costar_data.py --file data/costar_q4_2024.csv
  
  # Process all files in a directory
  python scripts/ingest_costar_data.py --directory data/costar_files/
  
  # Process directory recursively
  python scripts/ingest_costar_data.py --directory data/ --recursive
  
  # Validate files without importing
  python scripts/ingest_costar_data.py --file data/costar_q4_2024.csv --validate-only
  
  # Batch process with verbose logging
  python scripts/ingest_costar_data.py --directory data/ --verbose
        """,
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--file", "-f", type=Path, help="Process a single CoStar data file"
    )
    input_group.add_argument(
        "--directory",
        "-d",
        type=Path,
        help="Process all CoStar data files in a directory",
    )

    # Processing options
    parser.add_argument(
        "--recursive", "-r", action="store_true", help="Process directories recursively"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate files without importing to database",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without actually processing",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    logger.info("Starting CoStar data ingestion script")

    try:
        # Initialize CoStar MCP server
        if not args.validate_only and not args.dry_run:
            logger.info("Initializing CoStar MCP server...")
            server = CoStarMCPServer()
            await server.initialize()
            logger.info("CoStar MCP server initialized successfully")

        results = []

        if args.file:
            # Process single file
            if args.dry_run:
                logger.info(f"Would process file: {args.file}")
                return

            if args.validate_only:
                logger.info(f"Validating file: {args.file}")
                validation = await validate_file(args.file)

                if validation["valid"]:
                    logger.info("✅ File validation passed")
                    logger.info(f"   Records: {validation['record_count']}")
                    logger.info(f"   Columns: {', '.join(validation['columns'])}")
                else:
                    logger.error("❌ File validation failed")
                    for error in validation["errors"]:
                        logger.error(f"   Error: {error}")

                for warning in validation["warnings"]:
                    logger.warning(f"   Warning: {warning}")
            else:
                result = await process_single_file(server, args.file)
                results.append(result)

        elif args.directory:
            # Process directory
            if args.dry_run:
                # Find files that would be processed
                patterns = ["*.csv", "*.xlsx", "*.xls"]
                files = []

                for pattern in patterns:
                    if args.recursive:
                        files.extend(args.directory.rglob(pattern))
                    else:
                        files.extend(args.directory.glob(pattern))

                logger.info(f"Would process {len(files)} files from {args.directory}")
                for file_path in sorted(files):
                    logger.info(f"  - {file_path}")
                return

            if args.validate_only:
                # Validate all files in directory
                patterns = ["*.csv", "*.xlsx", "*.xls"]
                files = []

                for pattern in patterns:
                    if args.recursive:
                        files.extend(args.directory.rglob(pattern))
                    else:
                        files.extend(args.directory.glob(pattern))

                logger.info(f"Validating {len(files)} files")

                valid_count = 0
                for file_path in sorted(files):
                    validation = await validate_file(file_path)

                    if validation["valid"]:
                        logger.info(
                            f"✅ {file_path.name} - {validation['record_count']} records"
                        )
                        valid_count += 1
                    else:
                        logger.error(f"❌ {file_path.name}")
                        for error in validation["errors"]:
                            logger.error(f"   Error: {error}")

                logger.info(
                    f"Validation complete: {valid_count}/{len(files)} files valid"
                )
            else:
                results = await process_directory(
                    server, args.directory, args.recursive
                )

        # Summary report
        if results and not args.validate_only:
            logger.info("\n" + "=" * 50)
            logger.info("INGESTION SUMMARY")
            logger.info("=" * 50)

            total_processed = sum(r.records_processed for r in results)
            total_imported = sum(r.records_imported for r in results)
            total_failed = sum(r.records_failed for r in results)
            successful_files = len([r for r in results if r.import_status == "success"])

            logger.info(f"Files processed: {len(results)}")
            logger.info(f"Successful imports: {successful_files}")
            logger.info(f"Total records processed: {total_processed}")
            logger.info(f"Total records imported: {total_imported}")
            logger.info(f"Total records failed: {total_failed}")

            if total_processed > 0:
                success_rate = (total_imported / total_processed) * 100
                logger.info(f"Success rate: {success_rate:.1f}%")

        logger.info("CoStar data ingestion script completed successfully")

    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Script failed with error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        if "server" in locals():
            try:
                await server.close()
            except:
                pass


if __name__ == "__main__":
    asyncio.run(main())
