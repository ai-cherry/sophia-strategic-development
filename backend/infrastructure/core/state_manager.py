#!/usr/bin/env python3
"""
Sophia AI - Infrastructure State Manager
Manages the state of all infrastructure platforms and configurations
"""

import os
import json
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class StateCheckpoint:
    """Represents a configuration checkpoint for rollback purposes."""
    id: str
    platform: str
    configuration: Dict[str, Any]
    timestamp: datetime
    description: str
    
class InfrastructureStateManager:
    """
    Manages the persistent state of all infrastructure platforms.
    Provides checkpointing, rollback, and state tracking capabilities.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.path.join(
            Path(__file__).parent.parent.parent.parent,
            "data", "infrastructure_state.db"
        )
        self._ensure_db_directory()
        self._initialize_database()
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _initialize_database(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Platform state table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS platform_state (
                    platform TEXT PRIMARY KEY,
                    configuration TEXT,
                    status TEXT,
                    last_updated TIMESTAMP,
                    metrics TEXT,
                    dependencies TEXT
                )
            """)
            
            # Checkpoints table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id TEXT PRIMARY KEY,
                    platform TEXT,
                    configuration TEXT,
                    timestamp TIMESTAMP,
                    description TEXT
                )
            """)
            
            # Change history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS change_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT,
                    change_type TEXT,
                    old_config TEXT,
                    new_config TEXT,
                    timestamp TIMESTAMP,
                    user TEXT,
                    rollback_checkpoint TEXT
                )
            """)
            
            # Dependencies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS platform_dependencies (
                    platform TEXT,
                    depends_on TEXT,
                    dependency_type TEXT,
                    created_at TIMESTAMP,
                    PRIMARY KEY (platform, depends_on)
                )
            """)
            
            conn.commit()
    
    async def update_platform_state(
        self, 
        platform: str, 
        configuration: Dict[str, Any],
        status: str = "configured",
        metrics: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None
    ) -> bool:
        """Update the state of a platform."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO platform_state 
                    (platform, configuration, status, last_updated, metrics, dependencies)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    platform,
                    json.dumps(configuration),
                    status,
                    datetime.now(),
                    json.dumps(metrics or {}),
                    json.dumps(dependencies or [])
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Failed to update platform state for {platform}: {e}")
            return False
    
    async def get_platform_state(self, platform: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a platform."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT configuration, status, last_updated, metrics, dependencies
                    FROM platform_state WHERE platform = ?
                """, (platform,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "platform": platform,
                        "configuration": json.loads(row[0]),
                        "status": row[1],
                        "last_updated": row[2],
                        "metrics": json.loads(row[3]),
                        "dependencies": json.loads(row[4])
                    }
                
                return None
                
        except Exception as e:
            print(f"Failed to get platform state for {platform}: {e}")
            return None
    
    async def create_checkpoint(
        self, 
        platform: str, 
        configuration: Dict[str, Any],
        description: str = "Auto-generated checkpoint"
    ) -> str:
        """Create a configuration checkpoint for rollback purposes."""
        try:
            checkpoint_id = f"{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO checkpoints (id, platform, configuration, timestamp, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    checkpoint_id,
                    platform,
                    json.dumps(configuration),
                    datetime.now(),
                    description
                ))
                
                conn.commit()
                return checkpoint_id
                
        except Exception as e:
            print(f"Failed to create checkpoint for {platform}: {e}")
            return ""
    
    async def get_checkpoint(self, platform: str, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific checkpoint configuration."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT configuration, timestamp, description
                    FROM checkpoints WHERE platform = ? AND id = ?
                """, (platform, checkpoint_id))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "id": checkpoint_id,
                        "platform": platform,
                        "configuration": json.loads(row[0]),
                        "timestamp": row[1],
                        "description": row[2]
                    }
                
                return None
                
        except Exception as e:
            print(f"Failed to get checkpoint {checkpoint_id} for {platform}: {e}")
            return None
    
    async def list_checkpoints(self, platform: str, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent checkpoints for a platform."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, timestamp, description
                    FROM checkpoints WHERE platform = ?
                    ORDER BY timestamp DESC LIMIT ?
                """, (platform, limit))
                
                rows = cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        "platform": platform,
                        "timestamp": row[1],
                        "description": row[2]
                    }
                    for row in rows
                ]
                
        except Exception as e:
            print(f"Failed to list checkpoints for {platform}: {e}")
            return []
    
    async def record_change(
        self,
        platform: str,
        change_type: str,
        old_config: Dict[str, Any],
        new_config: Dict[str, Any],
        user: str = "system",
        rollback_checkpoint: Optional[str] = None
    ) -> bool:
        """Record a configuration change for audit purposes."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO change_history 
                    (platform, change_type, old_config, new_config, timestamp, user, rollback_checkpoint)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    platform,
                    change_type,
                    json.dumps(old_config),
                    json.dumps(new_config),
                    datetime.now(),
                    user,
                    rollback_checkpoint
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Failed to record change for {platform}: {e}")
            return False
    
    async def get_change_history(self, platform: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get change history for a platform."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT change_type, old_config, new_config, timestamp, user, rollback_checkpoint
                    FROM change_history WHERE platform = ?
                    ORDER BY timestamp DESC LIMIT ?
                """, (platform, limit))
                
                rows = cursor.fetchall()
                return [
                    {
                        "platform": platform,
                        "change_type": row[0],
                        "old_config": json.loads(row[1]),
                        "new_config": json.loads(row[2]),
                        "timestamp": row[3],
                        "user": row[4],
                        "rollback_checkpoint": row[5]
                    }
                    for row in rows
                ]
                
        except Exception as e:
            print(f"Failed to get change history for {platform}: {e}")
            return []
    
    async def set_platform_dependency(
        self, 
        platform: str, 
        depends_on: str, 
        dependency_type: str = "configuration"
    ) -> bool:
        """Set a dependency relationship between platforms."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO platform_dependencies 
                    (platform, depends_on, dependency_type, created_at)
                    VALUES (?, ?, ?, ?)
                """, (platform, depends_on, dependency_type, datetime.now()))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Failed to set dependency {platform} -> {depends_on}: {e}")
            return False
    
    async def get_platform_dependencies(self, platform: str) -> List[Dict[str, Any]]:
        """Get all dependencies for a platform."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT depends_on, dependency_type, created_at
                    FROM platform_dependencies WHERE platform = ?
                """, (platform,))
                
                rows = cursor.fetchall()
                return [
                    {
                        "platform": platform,
                        "depends_on": row[0],
                        "dependency_type": row[1],
                        "created_at": row[2]
                    }
                    for row in rows
                ]
                
        except Exception as e:
            print(f"Failed to get dependencies for {platform}: {e}")
            return []
    
    async def get_all_platform_states(self) -> Dict[str, Dict[str, Any]]:
        """Get the current state of all platforms."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT platform, configuration, status, last_updated, metrics, dependencies
                    FROM platform_state
                """)
                
                rows = cursor.fetchall()
                return {
                    row[0]: {
                        "configuration": json.loads(row[1]),
                        "status": row[2],
                        "last_updated": row[3],
                        "metrics": json.loads(row[4]),
                        "dependencies": json.loads(row[5])
                    }
                    for row in rows
                }
                
        except Exception as e:
            print(f"Failed to get all platform states: {e}")
            return {}
    
    async def cleanup_old_checkpoints(self, days_to_keep: int = 30) -> int:
        """Clean up old checkpoints to save space."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM checkpoints WHERE timestamp < ?
                """, (cutoff_date,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                return deleted_count
                
        except Exception as e:
            print(f"Failed to cleanup old checkpoints: {e}")
            return 0
    
    async def export_state(self, output_file: str) -> bool:
        """Export all infrastructure state to a JSON file."""
        try:
            all_states = await self.get_all_platform_states()
            
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "platform_states": all_states,
                "dependencies": {}
            }
            
            # Add dependency information
            for platform in all_states.keys():
                export_data["dependencies"][platform] = await self.get_platform_dependencies(platform)
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Failed to export state: {e}")
            return False
    
    async def import_state(self, input_file: str) -> bool:
        """Import infrastructure state from a JSON file."""
        try:
            with open(input_file, 'r') as f:
                import_data = json.load(f)
            
            # Import platform states
            for platform, state in import_data.get("platform_states", {}).items():
                await self.update_platform_state(
                    platform,
                    state["configuration"],
                    state["status"],
                    state.get("metrics"),
                    state.get("dependencies")
                )
            
            # Import dependencies
            for platform, deps in import_data.get("dependencies", {}).items():
                for dep in deps:
                    await self.set_platform_dependency(
                        platform,
                        dep["depends_on"],
                        dep["dependency_type"]
                    )
            
            return True
            
        except Exception as e:
            print(f"Failed to import state: {e}")
            return False

# CLI interface for state management
async def main():
    """CLI interface for infrastructure state management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Infrastructure State Manager")
    parser.add_argument("command", choices=["status", "checkpoints", "history", "export", "import", "cleanup"])
    parser.add_argument("--platform", help="Target platform")
    parser.add_argument("--file", help="File path for export/import")
    parser.add_argument("--limit", type=int, default=10, help="Limit for results")
    parser.add_argument("--days", type=int, default=30, help="Days to keep for cleanup")
    
    args = parser.parse_args()
    
    state_manager = InfrastructureStateManager()
    
    if args.command == "status":
        if args.platform:
            state = await state_manager.get_platform_state(args.platform)
            print(json.dumps(state, indent=2, default=str))
        else:
            states = await state_manager.get_all_platform_states()
            print(json.dumps(states, indent=2, default=str))
    
    elif args.command == "checkpoints":
        if not args.platform:
            print("Platform required for checkpoints command")
            return
        
        checkpoints = await state_manager.list_checkpoints(args.platform, args.limit)
        print(json.dumps(checkpoints, indent=2, default=str))
    
    elif args.command == "history":
        if not args.platform:
            print("Platform required for history command")
            return
        
        history = await state_manager.get_change_history(args.platform, args.limit)
        print(json.dumps(history, indent=2, default=str))
    
    elif args.command == "export":
        if not args.file:
            print("File path required for export command")
            return
        
        success = await state_manager.export_state(args.file)
        print(f"Export {'successful' if success else 'failed'}")
    
    elif args.command == "import":
        if not args.file:
            print("File path required for import command")
            return
        
        success = await state_manager.import_state(args.file)
        print(f"Import {'successful' if success else 'failed'}")
    
    elif args.command == "cleanup":
        deleted = await state_manager.cleanup_old_checkpoints(args.days)
        print(f"Cleaned up {deleted} old checkpoints")

if __name__ == "__main__":
    asyncio.run(main())

