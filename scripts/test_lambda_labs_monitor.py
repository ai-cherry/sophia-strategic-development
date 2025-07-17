#!/usr/bin/env python3
"""
Test script for Lambda Labs GPU Monitoring Agent

This script demonstrates the autonomous monitoring capabilities
of the Lambda Labs GPU monitoring agent.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from autonomous_agents.infrastructure.lambda_labs_monitor import LambdaLabsMonitorAgent
from autonomous_agents.monitoring.prometheus_exporter import exporter, collector


async def main():
    """Run the Lambda Labs monitoring agent test"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create agent instance
    agent = LambdaLabsMonitorAgent()
    
    # Register agent with metrics collector
    collector.register_agent("lambda_labs_monitor", agent)
    
    try:
        print("🚀 Starting Lambda Labs GPU Monitoring Agent Test")
        print("=" * 60)
        
        # Start Prometheus exporter
        print("\n📊 Starting Prometheus metrics exporter...")
        await exporter.start()
        print(f"✅ Prometheus metrics available at: http://localhost:{exporter.port}/metrics")
        
        # Start the monitoring agent
        print("\n🤖 Starting Lambda Labs monitoring agent...")
        await agent.start()
        print("✅ Agent started successfully")
        
        # Display initial status
        status = agent.get_status()
        print(f"\n📈 Agent Status:")
        print(f"  - Name: {status['name']}")
        print(f"  - Status: {status['status']}")
        print(f"  - Monitoring Interval: {status['monitoring_interval']}s")
        
        print("\n⏳ Running monitoring cycles (press Ctrl+C to stop)...")
        print("\n📋 Monitoring Output:")
        print("-" * 60)
        
        # Run for a few monitoring cycles
        cycles = 0
        while cycles < 3:  # Run 3 cycles for demo
            await asyncio.sleep(10)  # Wait 10 seconds between status updates
            
            # Get current metrics
            status = agent.get_status()
            recommendations = agent.get_optimization_recommendations()
            
            cycles += 1
            print(f"\n🔄 Monitoring Cycle {cycles}:")
            print(f"  - Monitoring Runs: {status['monitoring_runs']}")
            print(f"  - Monitoring Errors: {status['monitoring_errors']}")
            
            if recommendations:
                print(f"\n💡 Cost Optimization Recommendations:")
                for rec in recommendations:
                    print(f"  - Instance: {rec['instance_name']} ({rec['current_type']})")
                    print(f"    Average Utilization: {rec['avg_utilization']}")
                    print(f"    Recommendation: {rec['recommendation']}")
                    print(f"    Potential Savings: {rec['potential_monthly_savings']}")
            else:
                print(f"  - No optimization recommendations at this time")
        
        print("\n✅ Test completed successfully!")
        print(f"\n📊 Final Metrics Summary:")
        print(f"  - Total Monitoring Runs: {status['monitoring_runs']}")
        print(f"  - Total Monitoring Errors: {status['monitoring_errors']}")
        print(f"  - Error Rate: {(status['monitoring_errors'] / max(1, status['monitoring_runs'])) * 100:.1f}%")
        
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
        collector.unregister_agent("lambda_labs_monitor")
        
        # Stop Prometheus exporter
        await exporter.stop()
        print("✅ Prometheus exporter stopped")
        
        print("\n👋 Test complete!")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║          Lambda Labs GPU Monitoring Agent Test               ║
    ║                                                              ║
    ║  This test demonstrates autonomous GPU monitoring with:      ║
    ║  • Real-time GPU utilization tracking                        ║
    ║  • Anomaly detection (high/low usage)                        ║
    ║  • Cost optimization recommendations                         ║
    ║  • Prometheus metrics export                                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
