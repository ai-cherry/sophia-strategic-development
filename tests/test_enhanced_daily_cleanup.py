#!/usr/bin/env python3
"""
Integration tests for Enhanced Daily Cleanup
Tests dry-run, deletion, MCP scanning, and leak detection
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Add the scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts', 'utils'))

from enhanced_daily_cleanup import EnhancedDailyCleanup


class TestEnhancedDailyCleanup:
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            # Create directory structure
            (repo_path / "scripts" / "one_time").mkdir(parents=True)
            (repo_path / "scripts" / "utils").mkdir(parents=True)
            (repo_path / "mcp-servers" / "test_server").mkdir(parents=True)
            (repo_path / "mcp-servers" / "portkey_admin").mkdir(parents=True)
            (repo_path / "config").mkdir(parents=True)
            (repo_path / "docs").mkdir(parents=True)
            (repo_path / "backend").mkdir(parents=True)
            
            yield repo_path
    
    @pytest.fixture
    def cleanup_instance(self, temp_repo, monkeypatch):
        """Create cleanup instance with temp repo"""
        monkeypatch.chdir(temp_repo)
        cleanup = EnhancedDailyCleanup()
        cleanup.base_path = temp_repo
        return cleanup
    
    def test_dry_run_mode(self, cleanup_instance, temp_repo, monkeypatch):
        """Test that dry-run mode doesn't delete files"""
        # Set dry-run mode
        monkeypatch.setenv("DRY_RUN", "true")
        cleanup = EnhancedDailyCleanup()
        cleanup.base_path = temp_repo
        
        # Create a test file that should be deleted
        test_file = temp_repo / "test.backup"
        test_file.write_text("backup content")
        
        # Run cleanup
        result = cleanup.run_daily_cleanup()
        
        # Verify file still exists
        assert test_file.exists()
        assert cleanup.dry_run is True
        assert result["summary"]["cleanup_actions"] == 0
    
    def test_one_time_script_cleanup(self, cleanup_instance, temp_repo):
        """Test cleanup of expired one-time scripts"""
        scripts_dir = temp_repo / "scripts" / "one_time"
        
        # Create expired script
        expired_date = (datetime.now() - timedelta(days=5)).strftime("%Y_%m_%d")
        expired_script = scripts_dir / f"fix_issue_DELETE_{expired_date}.py"
        expired_script.write_text("#!/usr/bin/env python3\n# One-time fix")
        
        # Create future script (should not be deleted)
        future_date = (datetime.now() + timedelta(days=5)).strftime("%Y_%m_%d")
        future_script = scripts_dir / f"future_fix_DELETE_{future_date}.py"
        future_script.write_text("#!/usr/bin/env python3\n# Future fix")
        
        # Create old script without deletion date
        old_script = scripts_dir / "old_script.py"
        old_script.write_text("#!/usr/bin/env python3\n# Old script")
        # Make it old
        old_time = (datetime.now() - timedelta(days=40)).timestamp()
        os.utime(old_script, (old_time, old_time))
        
        cleanup_instance.dry_run = False
        result = cleanup_instance.run_daily_cleanup()
        
        # Verify results
        assert not expired_script.exists()
        assert future_script.exists()
        assert old_script.exists()  # Should warn but not delete
        assert len(result["findings"]["one_time_scripts"]) > 0
    
    def test_archive_directory_detection(self, cleanup_instance, temp_repo):
        """Test detection and removal of forbidden archive directories"""
        # Create empty archive directory
        empty_archive = temp_repo / "old_archive"
        empty_archive.mkdir()
        
        # Create non-empty backup directory
        backup_dir = temp_repo / "backup_2024"
        backup_dir.mkdir()
        (backup_dir / "important.txt").write_text("data")
        
        cleanup_instance.dry_run = False
        result = cleanup_instance.run_daily_cleanup()
        
        # Empty archive should be removed
        assert not empty_archive.exists()
        # Non-empty should still exist but be warned about
        assert backup_dir.exists()
        assert len([w for w in result["warnings"] if "backup_2024" in w]) > 0
    
    def test_backup_file_cleanup(self, cleanup_instance, temp_repo):
        """Test removal of backup files"""
        # Create various backup files
        backup_files = [
            temp_repo / "config.backup",
            temp_repo / "data.bak",
            temp_repo / "script.old",
            temp_repo / "temp.tmp",
        ]
        
        for bf in backup_files:
            bf.write_text("backup content")
        
        # Create a normal file
        normal_file = temp_repo / "important.py"
        normal_file.write_text("# Important code")
        
        cleanup_instance.dry_run = False
        result = cleanup_instance.run_daily_cleanup()
        
        # All backup files should be removed
        for bf in backup_files:
            assert not bf.exists()
        
        # Normal file should remain
        assert normal_file.exists()
        assert result["summary"]["total_files"] >= len(backup_files)
    
    def test_mcp_duplicate_detection(self, cleanup_instance, temp_repo):
        """Test MCP server duplicate detection"""
        # Create MCP config
        mcp_config = {
            "active_servers": {
                "test_server": 9000,
                "active_server": 9001
            },
            "removed_servers": ["portkey_admin", "old_server"],
            "unified_mcp_servers": {}
        }
        
        config_path = temp_repo / "config" / "consolidated_mcp_ports.json"
        with open(config_path, 'w') as f:
            json.dump(mcp_config, f)
        
        # Create removed server directory
        removed_server = temp_repo / "mcp-servers" / "old_server"
        removed_server.mkdir()
        (removed_server / "server.py").write_text("# Old server")
        
        result = cleanup_instance.run_daily_cleanup()
        
        # Should detect removed server
        duplicates = result["findings"]["mcp_duplicates"]
        assert len(duplicates) > 0
        assert any("old_server" in d["path"] for d in duplicates)
    
    def test_env_leak_detection(self, cleanup_instance, temp_repo):
        """Test detection of potential secret leaks"""
        # Create files with potential secrets
        env_file = temp_repo / ".env.test"
        env_file.write_text("""
API_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz
SECRET_TOKEN=super_secret_value_12345
NORMAL_VAR=not_a_secret
""")
        
        config_file = temp_repo / "config.json"
        config_file.write_text(json.dumps({
            "api_key": "sk-ant-12345678901234567890123456789012345678901234567890",
            "database_url": "postgresql://user:pass@localhost/db"
        }))
        
        script_file = temp_repo / "script.py"
        script_file.write_text("""
import os
# This is fine
api_key = os.getenv('API_KEY')
# This is bad
hardcoded_key = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
""")
        
        result = cleanup_instance.run_daily_cleanup()
        
        # Should detect leaks
        leaks = result["findings"]["env_leaks"]
        assert len(leaks) >= 2
        leak_paths = [leak["path"] for leak in leaks]
        assert any(".env.test" in path for path in leak_paths)
        assert any("config.json" in path for path in leak_paths)
    
    def test_stale_documentation_detection(self, cleanup_instance, temp_repo):
        """Test detection of stale documentation"""
        docs_dir = temp_repo / "docs"
        
        # Create old implementation doc
        old_doc = docs_dir / "implementation_guide.md"
        old_doc.write_text("# Old Implementation Guide")
        # Make it old
        old_time = (datetime.now() - timedelta(days=100)).timestamp()
        os.utime(old_doc, (old_time, old_time))
        
        # Create recent doc
        recent_doc = docs_dir / "deployment_plan.md"
        recent_doc.write_text("# Recent Deployment Plan")
        
        result = cleanup_instance.run_daily_cleanup()
        
        # Should detect stale doc
        stale_docs = result["findings"]["stale_documentation"]
        assert len(stale_docs) >= 1
        assert any("implementation_guide.md" in doc["path"] for doc in stale_docs)
    
    def test_large_file_detection(self, cleanup_instance, temp_repo):
        """Test detection of large files"""
        # Create a large file (simulate)
        large_file = temp_repo / "large_data.bin"
        # Write 11MB of data
        with open(large_file, 'wb') as f:
            f.write(b'0' * (11 * 1024 * 1024))
        
        result = cleanup_instance.run_daily_cleanup()
        
        # Should detect large file
        large_files = result["findings"]["large_files"]
        assert len(large_files) >= 1
        assert large_files[0]["size_mb"] > 10
    
    def test_protected_directories(self, cleanup_instance, temp_repo):
        """Test that protected directories are not touched"""
        # Create protected directories with forbidden names
        protected_dirs = [
            temp_repo / ".git" / "backup",
            temp_repo / "node_modules" / "old",
            temp_repo / ".venv" / "archive"
        ]
        
        for pd in protected_dirs:
            pd.mkdir(parents=True)
            (pd / "file.txt").write_text("protected")
        
        cleanup_instance.dry_run = False
        result = cleanup_instance.run_daily_cleanup()
        
        # All protected directories should still exist
        for pd in protected_dirs:
            assert pd.exists()
            assert (pd / "file.txt").exists()
    
    def test_json_report_generation(self, cleanup_instance, temp_repo):
        """Test JSON report generation"""
        # Create some test files
        (temp_repo / "test.backup").write_text("backup")
        
        result = cleanup_instance.run_daily_cleanup()
        
        # Check report was saved
        report_path = temp_repo / "cleanup_scan_report.json"
        assert report_path.exists()
        
        # Load and verify report
        with open(report_path) as f:
            report = json.load(f)
        
        assert "timestamp" in report
        assert "summary" in report
        assert "findings" in report
        assert report["dry_run"] is True
    
    def test_metrics_calculation(self, cleanup_instance, temp_repo):
        """Test accurate metrics calculation"""
        # Create files with known sizes
        file1 = temp_repo / "file1.backup"
        file1.write_text("x" * 1000)  # 1KB
        
        file2 = temp_repo / "file2.bak"
        file2.write_text("y" * 2000)  # 2KB
        
        archive_dir = temp_repo / "old_archive"
        archive_dir.mkdir()
        
        result = cleanup_instance.run_daily_cleanup()
        
        # Verify metrics
        assert result["summary"]["total_files"] >= 2
        assert result["summary"]["total_dirs"] >= 1
        assert result["summary"]["total_size_mb"] > 0
    
    @pytest.mark.parametrize("secret_pattern,test_string,should_match", [
        (r'sk-[a-zA-Z0-9]{48}', "sk-123456789012345678901234567890123456789012345678", True),
        (r'sk-ant-[a-zA-Z0-9\-]{40,}', "sk-ant-1234567890123456789012345678901234567890", True),
        (r'pul-[a-f0-9]{40}', "pul-FAKE1234567890abcdefFAKE1234567890abcd", True),
        (r'ghp_[a-zA-Z0-9]{36}', "ghp_123456789012345678901234567890123456", True),
        (r'(?i)api_key', "API_KEY=secret", True),
        (r'(?i)api_key', "normal_variable=value", False),
    ])
    def test_secret_patterns(self, secret_pattern, test_string, should_match):
        """Test secret detection patterns"""
        import re
        pattern = re.compile(secret_pattern)
        match = pattern.search(test_string)
        assert (match is not None) == should_match


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 