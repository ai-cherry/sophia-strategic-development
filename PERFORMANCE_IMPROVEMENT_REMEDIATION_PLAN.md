#!/usr/bin/env python3
"""
Performance Improvements Implementation Script
Implements the 5 critical performance improvements identified in the remediation plan
"""

import asyncio
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceImprovementImplementer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.improvements_applied = []
        self.backup_files = []
        
    def backup_file(self, file_path: Path) -> Path:
        """Create backup of file before modification"""
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup.{int(time.time())}")
        backup_path.write_text(file_path.read_text())
        self.backup_files.append(backup_path)
        logger.info(f"📁 Created backup: {backup_path}")
        return backup_path
    
    def apply_improvement_1_blocking_loops(self) -> bool:
        """Task 1: Convert blocking monitoring loops to async"""
        try:
            logger.info("🔧 Task 1: Converting blocking monitoring loops to async")
            
            files_to_fix = [
                "scripts/run_all_mcp_servers.py",
                "scripts/start_all_mcp_servers.py"
            ]
            
            for file_path_str in files_to_fix:
                file_path = self.project_root / file_path_str
                if not file_path.exists():
                    logger.warning(f"⚠️ File not found: {file_path}")
                    continue
                
                self.backup_file(file_path)
                content = file_path.read_text()
                
                # Pattern 1: Replace blocking while True with event-driven shutdown
                blocking_pattern = r'try:\s*\n\s*while True:\s*\n\s*time\.sleep\(1\)\s*\nexcept KeyboardInterrupt:'
                replacement = '''import signal
import asyncio

shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    logger.info("Shutdown signal received")
    shutdown_event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    await shutdown_event.wait()
except KeyboardInterrupt:'''
                
                if re.search(blocking_pattern, content, re.MULTILINE):
                    content = re.sub(blocking_pattern, replacement, content, flags=re.MULTILINE)
                    file_path.write_text(content)
                    logger.info(f"✅ Fixed blocking loop in {file_path}")
                    self.improvements_applied.append(f"Task 1: {file_path}")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Task 1 failed: {e}")
            return False
    
    def apply_improvement_2_infinite_sleep(self) -> bool:
        """Task 2: Replace infinite sleep with graceful event loop"""
        try:
            logger.info("🔧 Task 2: Replacing infinite sleep loops")
            
            file_path = self.project_root / "start_sophia_complete.py"
            if not file_path.exists():
                logger.warning(f"⚠️ File not found: {file_path}")
                return False
            
            self.backup_file(file_path)
            content = file_path.read_text()
            
            # Look for the infinite sleep pattern
            infinite_sleep_pattern = r'# Keep running\s*\n\s*while True:\s*\n\s*await asyncio\.sleep\(30\)'
            
            if re.search(infinite_sleep_pattern, content, re.MULTILINE):
                # Add shutdown event handling
                shutdown_code = '''# Graceful shutdown handling
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()

# Setup signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

logger.info("🎉 Sophia AI system is ready!")
logger.info("Press Ctrl+C to stop all services")

# Wait for shutdown signal instead of infinite sleep
try:
    await shutdown_event.wait()
except KeyboardInterrupt:
    logger.info("🛑 Shutdown requested")'''
                
                content = re.sub(infinite_sleep_pattern, shutdown_code, content, flags=re.MULTILINE)
                
                # Add signal import at the top if not present
                if 'import signal' not in content:
                    content = content.replace('import asyncio', 'import asyncio\nimport signal')
                
                file_path.write_text(content)
                logger.info(f"✅ Fixed infinite sleep loop in {file_path}")
                self.improvements_applied.append(f"Task 2: {file_path}")
                return True
            else:
                logger.info("📝 Infinite sleep pattern not found - may already be fixed")
                return True
                
        except Exception as e:
            logger.error(f"❌ Task 2 failed: {e}")
            return False
    
    def apply_improvement_3_health_checks(self) -> bool:
        """Task 3: Make health check workers interruptible"""
        try:
            logger.info("🔧 Task 3: Making health check workers interruptible")
            
            # Search for connection pool managers
            pool_files = list(self.project_root.rglob("*connection_pool*.py"))
            
            for file_path in pool_files:
                if not file_path.exists():
                    continue
                    
                self.backup_file(file_path)
                content = file_path.read_text()
                
                # Look for health check worker pattern
                health_check_pattern = r'def _health_check_worker\(self\):\s*\n\s*while not self\._shutdown:\s*\n.*?time\.sleep\(.*?\)'
                
                if re.search(health_check_pattern, content, re.MULTILINE | re.DOTALL):
                    # Add shutdown event to __init__ if not present
                    if 'self._shutdown_event = threading.Event()' not in content:
                        init_pattern = r'(def __init__\(self.*?\):.*?\n)'
                        init_replacement = r'\1        self._shutdown_event = threading.Event()\n'
                        content = re.sub(init_pattern, init_replacement, content, flags=re.MULTILINE | re.DOTALL)
                    
                    # Replace blocking sleep with interruptible wait
                    sleep_pattern = r'time\.sleep\(self\.config\.health_check_interval\)'
                    sleep_replacement = '''if self._shutdown_event.wait(timeout=self.config.health_check_interval):
                break  # Shutdown requested'''
                    
                    content = re.sub(sleep_pattern, sleep_replacement, content)
                    
                    # Add threading import if not present
                    if 'import threading' not in content:
                        content = 'import threading\n' + content
                    
                    file_path.write_text(content)
                    logger.info(f"✅ Fixed health check worker in {file_path}")
                    self.improvements_applied.append(f"Task 3: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Task 3 failed: {e}")
            return False
    
    def apply_improvement_4_chunked_processing(self) -> bool:
        """Task 4: Stream database records in chunks"""
        try:
            logger.info("🔧 Task 4: Implementing chunked database processing")
            
            file_path = self.project_root / "backend/etl/payready_core/ingest_core_sql_data.py"
            if not file_path.exists():
                logger.warning(f"⚠️ File not found: {file_path}")
                return False
            
            self.backup_file(file_path)
            content = file_path.read_text()
            
            # Add chunk_size to config if not present
            config_pattern = r'(@dataclass\s*\nclass PayReadyDataIngestionConfig:.*?)(batch_size: int = 1000)'
            config_replacement = r'\1\2\n    chunk_size: int = 10000  # Configurable chunk size\n    max_memory_usage_mb: int = 500  # Memory limit'
            
            if re.search(config_pattern, content, re.MULTILINE | re.DOTALL):
                content = re.sub(config_pattern, config_replacement, content, flags=re.MULTILINE | re.DOTALL)
            
            # Add chunked processing method
            chunked_method = '''
    async def extract_payment_transactions_chunked(
        self, since_date: datetime | None = None
    ) -> AsyncGenerator[pd.DataFrame, None]:
        """Extract payment transactions in chunks to reduce memory usage"""
        try:
            if since_date is None:
                since_date = datetime.now() - timedelta(
                    hours=self.config.sync_window_hours
                )

            # Count total records first
            count_query = """
            SELECT COUNT(*) as total_count
            FROM payment_transactions
            WHERE processing_date >= :since_date
            OR updated_at >= :since_date
            """
            
            total_result = pd.read_sql_query(
                text(count_query), self.source_engine, params={"since_date": since_date}
            )
            total_records = total_result.iloc[0]['total_count']
            
            logger.info(f"📊 Processing {total_records} payment transactions in chunks of {self.config.chunk_size}")

            # Process in chunks with OFFSET/LIMIT
            offset = 0
            chunk_num = 0
            
            while offset < total_records:
                chunk_query = """
                SELECT
                    transaction_id, customer_id, amount, currency, transaction_type,
                    payment_method, status, processing_date, completed_date, failure_reason,
                    property_id, unit_id, lease_id, invoice_id, processor_name,
                    processor_transaction_id, processor_fee, processing_time_ms,
                    risk_score, fraud_flags, compliance_status, aml_status,
                    created_at, created_by, updated_by
                FROM payment_transactions
                WHERE processing_date >= :since_date
                OR updated_at >= :since_date
                ORDER BY processing_date DESC
                LIMIT :chunk_size OFFSET :offset
                """

                chunk_df = pd.read_sql_query(
                    text(chunk_query), 
                    self.source_engine, 
                    params={
                        "since_date": since_date,
                        "chunk_size": self.config.chunk_size,
                        "offset": offset
                    }
                )

                if chunk_df.empty:
                    break

                chunk_num += 1
                logger.info(f"📦 Processing chunk {chunk_num}: {len(chunk_df)} records (offset: {offset})")
                
                yield chunk_df
                
                offset += self.config.chunk_size
                
                # Memory management - force garbage collection
                import gc
                gc.collect()

        except Exception as e:
            logger.error(f"❌ Failed to extract payment transactions in chunks: {e}")
            raise
'''
            
            # Add the method before the existing extract method
            extract_pattern = r'(async def extract_payment_transactions\()'
            content = re.sub(extract_pattern, chunked_method + '\n    \\1', content)
            
            # Add AsyncGenerator import if not present
            if 'AsyncGenerator' not in content:
                content = content.replace('from typing import', 'from typing import AsyncGenerator,')
            
            file_path.write_text(content)
            logger.info(f"✅ Added chunked processing to {file_path}")
            self.improvements_applied.append(f"Task 4: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Task 4 failed: {e}")
            return False
    
    def apply_improvement_5_bounded_retries(self) -> bool:
        """Task 5: Limit retries in HTTP request helper"""
        try:
            logger.info("🔧 Task 5: Adding bounded retries to HTTP requests")
            
            file_path = self.project_root / "backend/integrations/gong_api_client_enhanced.py"
            if not file_path.exists():
                logger.warning(f"⚠️ File not found: {file_path}")
                return False
            
            self.backup_file(file_path)
            content = file_path.read_text()
            
            # Look for the infinite while True loop
            infinite_while_pattern = r'while True:\s*\n\s*try:'
            
            if re.search(infinite_while_pattern, content):
                # Replace with bounded loop
                bounded_replacement = '''attempt = 0
        max_attempts = kwargs.get('max_attempts', 5)
        
        while attempt < max_attempts:
            try:'''
                
                content = re.sub(infinite_while_pattern, bounded_replacement, content)
                
                # Add attempt increment and max check
                attempt_pattern = r'await asyncio\.sleep\(retry_delay\)\s*\n\s*attempt \+= 1'
                attempt_replacement = '''await asyncio.sleep(retry_delay)
                attempt += 1
                
        # All retries exhausted
        if last_error:
            logger.error(f"Request failed after {max_attempts} attempts: {last_error}")
            raise last_error
        else:
            raise Exception(f"Request failed after {max_attempts} attempts")'''
                
                content = re.sub(attempt_pattern, attempt_replacement, content)
                
                file_path.write_text(content)
                logger.info(f"✅ Added bounded retries to {file_path}")
                self.improvements_applied.append(f"Task 5: {file_path}")
                return True
            else:
                logger.info("📝 Infinite retry loop not found - may already be fixed")
                return True
                
        except Exception as e:
            logger.error(f"❌ Task 5 failed: {e}")
            return False
    
    def validate_improvements(self) -> Dict[str, bool]:
        """Validate that improvements were applied correctly"""
        logger.info("🧪 Validating improvements...")
        
        validation_results = {}
        
        # Test 1: Check for blocking loops
        validation_results['blocking_loops'] = self._validate_no_blocking_loops()
        
        # Test 2: Check for infinite sleeps
        validation_results['infinite_sleeps'] = self._validate_no_infinite_sleeps()
        
        # Test 3: Check for interruptible health checks
        validation_results['health_checks'] = self._validate_interruptible_health_checks()
        
        # Test 4: Check for chunked processing
        validation_results['chunked_processing'] = self._validate_chunked_processing()
        
        # Test 5: Check for bounded retries
        validation_results['bounded_retries'] = self._validate_bounded_retries()
        
        return validation_results
    
    def _validate_no_blocking_loops(self) -> bool:
        """Check that blocking while True loops are removed"""
        blocking_files = [
            "scripts/run_all_mcp_servers.py",
            "scripts/start_all_mcp_servers.py"
        ]
        
        for file_path_str in blocking_files:
            file_path = self.project_root / file_path_str
            if file_path.exists():
                content = file_path.read_text()
                if 'while True:' in content and 'time.sleep(1)' in content:
                    return False
        return True
    
    def _validate_no_infinite_sleeps(self) -> bool:
        """Check that infinite sleep loops are removed"""
        file_path = self.project_root / "start_sophia_complete.py"
        if file_path.exists():
            content = file_path.read_text()
            return not ('while True:' in content and 'await asyncio.sleep(30)' in content)
        return True
    
    def _validate_interruptible_health_checks(self) -> bool:
        """Check that health checks use interruptible waits"""
        pool_files = list(self.project_root.rglob("*connection_pool*.py"))
        
        for file_path in pool_files:
            if file_path.exists():
                content = file_path.read_text()
                if '_health_check_worker' in content:
                    if 'time.sleep(' in content and '_shutdown_event.wait(' not in content:
                        return False
        return True
    
    def _validate_chunked_processing(self) -> bool:
        """Check that chunked processing is implemented"""
        file_path = self.project_root / "backend/etl/payready_core/ingest_core_sql_data.py"
        if file_path.exists():
            content = file_path.read_text()
            return 'extract_payment_transactions_chunked' in content
        return True
    
    def _validate_bounded_retries(self) -> bool:
        """Check that retry loops are bounded"""
        file_path = self.project_root / "backend/integrations/gong_api_client_enhanced.py"
        if file_path.exists():
            content = file_path.read_text()
            return not ('while True:' in content and 'attempt +=' in content)
        return True
    
    def generate_report(self, validation_results: Dict[str, bool]) -> str:
        """Generate implementation report"""
        report = f"""
# 🎉 Performance Improvements Implementation Report

**Date**: {datetime.now().isoformat()}
**Total Improvements Applied**: {len(self.improvements_applied)}

## ✅ Applied Improvements:
"""
        
        for improvement in self.improvements_applied:
            report += f"- {improvement}\n"
        
        report += "\n## 🧪 Validation Results:\n"
        
        for test_name, passed in validation_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            report += f"- {test_name}: {status}\n"
        
        overall_success = all(validation_results.values())
        report += f"\n## 📊 Overall Status: {'✅ SUCCESS' if overall_success else '❌ NEEDS ATTENTION'}\n"
        
        if self.backup_files:
            report += "\n## 📁 Backup Files Created:\n"
            for backup in self.backup_files:
                report += f"- {backup}\n"
        
        return report
    
    async def run_implementation(self) -> bool:
        """Run all performance improvements"""
        logger.info("🚀 Starting Performance Improvements Implementation")
        
        start_time = time.time()
        
        # Apply all improvements
        tasks = [
            ("Task 1: Blocking Loops", self.apply_improvement_1_blocking_loops),
            ("Task 2: Infinite Sleep", self.apply_improvement_2_infinite_sleep),
            ("Task 3: Health Checks", self.apply_improvement_3_health_checks),
            ("Task 4: Chunked Processing", self.apply_improvement_4_chunked_processing),
            ("Task 5: Bounded Retries", self.apply_improvement_5_bounded_retries),
        ]
        
        success_count = 0
        for task_name, task_func in tasks:
            logger.info(f"📋 Executing {task_name}")
            if task_func():
                success_count += 1
                logger.info(f"✅ {task_name} completed successfully")
            else:
                logger.error(f"❌ {task_name} failed")
        
        # Validate improvements
        validation_results = self.validate_improvements()
        
        # Generate report
        report = self.generate_report(validation_results)
        
        # Save report
        report_path = self.project_root / "PERFORMANCE_IMPROVEMENTS_REPORT.md"
        report_path.write_text(report)
        
        execution_time = time.time() - start_time
        
        logger.info(f"🎉 Implementation completed in {execution_time:.2f}s")
        logger.info(f"📊 Success rate: {success_count}/{len(tasks)} tasks")
        logger.info(f"📄 Report saved to: {report_path}")
        
        return success_count == len(tasks) and all(validation_results.values())


async def main():
    """Main execution function"""
    implementer = PerformanceImprovementImplementer()
    
    try:
        success = await implementer.run_implementation()
        
        if success:
            print("🎉 All performance improvements implemented successfully!")
            return 0
        else:
            print("⚠️ Some improvements failed or need attention")
            return 1
            
    except Exception as e:
        logger.error(f"💥 Implementation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 