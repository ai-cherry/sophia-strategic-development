#!/usr/bin/env python3
"""
Test script for the Qdrant Optimizer Autonomous Agent

This demonstrates how the agent autonomously monitors and optimizes
Qdrant vector database performance.
"""

import asyncio
import logging

from autonomous_agents.infrastructure.qdrant_optimizer import QdrantOptimizerAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_qdrant_optimizer():
    """Test the Qdrant optimizer agent"""
    print("\n🚀 Starting Qdrant Optimizer Agent Test")
    print("="*60)
    
    # Create agent in dry-run mode for testing
    agent = QdrantOptimizerAgent(dry_run=True)
    
    try:
        # Initialize the agent
        print("\n📊 Initializing agent...")
        await agent.initialize()
        print(f"✅ Agent initialized: {agent.name}")
        print(f"   Status: {agent.status.value}")
        print(f"   Dry run mode: {agent.dry_run}")
        
        # Run monitoring cycle
        print("\n🔍 Running monitoring cycle...")
        await agent.monitor()
        
        # Show optimization summary
        print("\n📈 Optimization Summary:")
        summary = agent.get_optimization_summary()
        
        print(f"\n   Total optimizations attempted: {summary['total_optimizations']}")
        print(f"   Successful: {summary['successful']}")
        print(f"   Failed: {summary['failed']}")
        print(f"   Dry run mode: {summary['dry_run_mode']}")
        
        if summary['optimizations_by_type']:
            print("\n   Optimizations by type:")
            for action_type, count in summary['optimizations_by_type'].items():
                print(f"   - {action_type}: {count}")
        
        if summary['collections']:
            print("\n   Collection statistics:")
            for collection, stats in summary['collections'].items():
                print(f"\n   📦 {collection}:")
                print(f"      Vectors: {stats['vector_count']:,}")
                print(f"      Disk usage: {stats['disk_usage_gb']:.2f} GB")
                print(f"      Memory usage: {stats['memory_usage_gb']:.2f} GB")
                print(f"      Avg query latency: {stats['avg_query_latency_ms']:.1f} ms")
                print(f"      Last optimized: {stats['last_optimized']}")
        
        # Simulate multiple monitoring cycles
        print("\n🔄 Running additional monitoring cycles...")
        for i in range(3):
            await asyncio.sleep(2)  # Wait between cycles
            print(f"\n   Cycle {i+2}...")
            await agent.monitor()
        
        # Show final summary
        print("\n📊 Final Optimization Summary:")
        final_summary = agent.get_optimization_summary()
        print(f"   Total optimization actions evaluated: {final_summary['total_optimizations']}")
        
        # Show optimization history
        if agent.optimization_history:
            print("\n📜 Optimization History:")
            for action in agent.optimization_history[-5:]:  # Show last 5
                print(f"\n   • {action.action_type.value} on {action.collection_name}")
                print(f"     Reason: {action.reason}")
                print(f"     Impact: {action.estimated_impact}")
                print(f"     Priority: {'High' if action.priority == 2 else 'Medium' if action.priority == 1 else 'Low'}")
                print(f"     Status: {action.status}")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.exception("Test failed")
        raise
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        await agent.cleanup()
        print("✅ Cleanup complete")


async def test_real_mode():
    """Test the agent in real mode (be careful!)"""
    print("\n⚠️  WARNING: Running in REAL MODE")
    print("This will make actual changes to your Qdrant instance!")
    
    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Test cancelled.")
        return
    
    agent = QdrantOptimizerAgent(dry_run=False)
    
    try:
        await agent.initialize()
        print("\n✅ Agent initialized in REAL mode")
        
        # Run one monitoring cycle
        await agent.monitor()
        
        # Show what was done
        summary = agent.get_optimization_summary()
        print("\n📊 Actions taken:")
        print(f"   Successful: {summary['successful']}")
        print(f"   Failed: {summary['failed']}")
        
    finally:
        await agent.cleanup()


async def main():
    """Main test function"""
    print("\n🎯 Qdrant Optimizer Autonomous Agent Test Suite")
    print("="*60)
    
    # Test in dry-run mode
    await test_qdrant_optimizer()
    
    # Optionally test in real mode
    # print("\n" + "="*60)
    # await test_real_mode()


if __name__ == "__main__":
    asyncio.run(main())
