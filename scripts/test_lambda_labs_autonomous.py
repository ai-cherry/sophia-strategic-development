#!/usr/bin/env python3
"""
Test script for Lambda Labs Autonomous GPU Management Agent

This script demonstrates the autonomous action capabilities including:
- Automatic instance provisioning during high demand
- Automatic instance termination for idle resources
- Cost optimization with safety controls
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from autonomous_agents.infrastructure.lambda_labs_autonomous import (
    LambdaLabsAutonomousAgent,
    ActionType,
    ActionStatus
)
from autonomous_agents.monitoring.prometheus_exporter import exporter, collector


async def main(dry_run: bool = True):
    """Run the Lambda Labs autonomous agent test"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create agent instance
    agent = LambdaLabsAutonomousAgent(dry_run=dry_run)
    
    # Register agent with metrics collector
    collector.register_agent("lambda_labs_autonomous", agent)
    
    try:
        print("🚀 Starting Lambda Labs Autonomous GPU Management Agent Test")
        print("=" * 70)
        print(f"🔧 Mode: {'DRY RUN' if dry_run else 'LIVE'} mode")
        print(f"💰 Max hourly spend: ${agent.max_hourly_spend}")
        print(f"📊 Max instances: {agent.max_instances}")
        print(f"⏱️  Action cooldown: {agent.action_cooldown_mins} minutes")
        print(f"💵 Confirmation threshold: ${agent.confirmation_threshold}/hour")
        print("=" * 70)
        
        # Start Prometheus exporter
        print("\n📊 Starting Prometheus metrics exporter...")
        await exporter.start()
        print(f"✅ Prometheus metrics available at: http://localhost:{exporter.port}/metrics")
        
        # Start the autonomous agent
        print("\n🤖 Starting Lambda Labs autonomous agent...")
        await agent.start()
        print("✅ Agent started successfully")
        
        # Display initial status
        status = agent.get_status()
        print(f"\n📈 Agent Status:")
        print(f"  - Name: {status['name']}")
        print(f"  - Status: {status['status']}")
        print(f"  - Monitoring Interval: {status['monitoring_interval']}s")
        
        print("\n⏳ Running autonomous monitoring cycles (press Ctrl+C to stop)...")
        print("\n📋 Autonomous Actions Log:")
        print("-" * 70)
        
        # Run for a few monitoring cycles
        cycles = 0
        while cycles < 5:  # Run 5 cycles for demo
            await asyncio.sleep(10)  # Wait 10 seconds between status updates
            
            # Get current status
            status = agent.get_status()
            action_summary = agent.get_action_summary()
            
            cycles += 1
            print(f"\n🔄 Monitoring Cycle {cycles}:")
            print(f"  - Monitoring Runs: {status['monitoring_runs']}")
            print(f"  - Monitoring Errors: {status['monitoring_errors']}")
            print(f"  - Instances Running: {action_summary['instances_running']}/{action_summary['max_instances']}")
            print(f"  - Current Hourly Spend: ${action_summary['current_hourly_spend']:.2f}/${action_summary['max_hourly_spend']}")
            
            if action_summary['total_actions'] > 0:
                print(f"\n💡 Autonomous Actions Summary:")
                print(f"  - Total Actions: {action_summary['total_actions']}")
                print(f"  - Successful: {action_summary['successful_actions']}")
                print(f"  - Failed: {action_summary['failed_actions']}")
                print(f"  - Pending Confirmations: {action_summary['pending_confirmations']}")
                print(f"  - Total Cost Impact: ${action_summary['total_cost_impact']:.2f}/hour")
                
                print(f"\n  Actions by Type:")
                for action_type, count in action_summary['actions_by_type'].items():
                    if count > 0:
                        print(f"    - {action_type}: {count}")
            
            # Display recent actions from history
            if agent.action_history:
                print(f"\n📜 Recent Actions:")
                for history in agent.action_history[-3:]:  # Show last 3 actions
                    action = history.action
                    print(f"  - [{action.status.value}] {action.action_type.value}")
                    print(f"    Reason: {action.reason}")
                    print(f"    Cost Impact: ${action.estimated_cost_impact:.2f}/hour")
                    if action.executed_at:
                        print(f"    Executed: {action.executed_at.strftime('%H:%M:%S')}")
        
        print("\n✅ Test completed successfully!")
        
        # Final summary
        final_summary = agent.get_action_summary()
        print(f"\n📊 Final Autonomous Agent Summary:")
        print(f"  - Total Monitoring Runs: {status['monitoring_runs']}")
        print(f"  - Total Actions Taken: {final_summary['total_actions']}")
        print(f"  - Successful Actions: {final_summary['successful_actions']}")
        print(f"  - Failed Actions: {final_summary['failed_actions']}")
        print(f"  - Safety Blocks: Check Prometheus metrics for details")
        print(f"  - Total Cost Impact: ${final_summary['total_cost_impact']:.2f}/hour")
        
        if dry_run:
            print("\n⚠️  Note: This was a DRY RUN - no actual instances were created or terminated")
            print("    To run in LIVE mode, use: --live")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.exception("Test failed")
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        
        # Stop agent
        await agent.stop()
        print("✅ Agent stopped")
        
        # Unregister from collector
        collector.unregister_agent("lambda_labs_autonomous")
        
        # Stop Prometheus exporter
        await exporter.stop()
        print("✅ Prometheus exporter stopped")
        
        print("\n👋 Test complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Lambda Labs Autonomous GPU Management Agent")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run in LIVE mode (actually create/terminate instances)"
    )
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║      Lambda Labs Autonomous GPU Management Agent Test        ║
    ║                                                              ║
    ║  This test demonstrates autonomous GPU management with:      ║
    ║  • Automatic instance provisioning during high demand        ║
    ║  • Automatic termination of idle instances                   ║
    ║  • Cost optimization with spending limits                    ║
    ║  • Safety mechanisms and confirmation workflows              ║
    ║  • Full audit trail and rollback capabilities               ║
    ║                                                              ║
    ║  Safety Features:                                            ║
    ║  • Max hourly spend limits                                   ║
    ║  • Instance count limits                                     ║
    ║  • Cooldown periods between actions                          ║
    ║  • Confirmation for high-cost actions                        ║
    ║  • Dry-run mode for testing                                  ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    if args.live:
        print("\n⚠️  WARNING: Running in LIVE mode - this will create/terminate real instances!")
        print("    Cost charges will apply. Press Ctrl+C within 5 seconds to cancel...")
        try:
            asyncio.run(asyncio.sleep(5))
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            sys.exit(1)
    
    asyncio.run(main(dry_run=not args.live))
