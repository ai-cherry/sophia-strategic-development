#!/usr/bin/env python3
"""
Phase 4: n8n Cache Eviction Optimization
Optimizes cache eviction for >85% cache hits

Date: July 12, 2025
"""

import asyncio
import json
import logging
import random
import time
from collections import OrderedDict
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class CacheSimulator:
    """Simulate different cache eviction strategies"""
    
    def __init__(self, cache_size: int = 1000):
        self.cache_size = cache_size
        self.strategies = ["lru", "lfu", "fifo", "adaptive"]
        self.results = {}
        
    def generate_access_pattern(self, num_requests: int = 10000) -> List[str]:
        """Generate realistic access pattern with hot/cold data"""
        # 80/20 rule: 80% of requests go to 20% of items
        hot_items = [f"hot_item_{i}" for i in range(200)]
        cold_items = [f"cold_item_{i}" for i in range(800)]
        
        pattern = []
        for _ in range(num_requests):
            if random.random() < 0.8:  # 80% chance
                pattern.append(random.choice(hot_items))
            else:
                pattern.append(random.choice(cold_items))
        
        return pattern
    
    def simulate_lru(self, access_pattern: List[str]) -> Dict[str, Any]:
        """Simulate LRU (Least Recently Used) cache"""
        cache = OrderedDict()
        hits = 0
        misses = 0
        
        for item in access_pattern:
            if item in cache:
                hits += 1
                # Move to end (most recent)
                cache.move_to_end(item)
            else:
                misses += 1
                cache[item] = True
                # Evict oldest if cache full
                if len(cache) > self.cache_size:
                    cache.popitem(last=False)
        
        hit_rate = hits / (hits + misses)
        return {
            "strategy": "lru",
            "hits": hits,
            "misses": misses,
            "hit_rate": hit_rate,
            "cache_size": len(cache)
        }
    
    def simulate_lfu(self, access_pattern: List[str]) -> Dict[str, Any]:
        """Simulate LFU (Least Frequently Used) cache"""
        cache = {}
        frequency = {}
        hits = 0
        misses = 0
        
        for item in access_pattern:
            if item in cache:
                hits += 1
                frequency[item] += 1
            else:
                misses += 1
                if len(cache) >= self.cache_size:
                    # Evict least frequent
                    min_freq_item = min(frequency.keys(), key=lambda k: frequency[k])
                    del cache[min_freq_item]
                    del frequency[min_freq_item]
                
                cache[item] = True
                frequency[item] = 1
        
        hit_rate = hits / (hits + misses)
        return {
            "strategy": "lfu",
            "hits": hits,
            "misses": misses,
            "hit_rate": hit_rate,
            "cache_size": len(cache)
        }
    
    def simulate_fifo(self, access_pattern: List[str]) -> Dict[str, Any]:
        """Simulate FIFO (First In First Out) cache"""
        cache = OrderedDict()
        hits = 0
        misses = 0
        
        for item in access_pattern:
            if item in cache:
                hits += 1
            else:
                misses += 1
                cache[item] = True
                # Evict oldest if cache full
                if len(cache) > self.cache_size:
                    cache.popitem(last=False)
        
        hit_rate = hits / (hits + misses)
        return {
            "strategy": "fifo",
            "hits": hits,
            "misses": misses,
            "hit_rate": hit_rate,
            "cache_size": len(cache)
        }
    
    def simulate_adaptive(self, access_pattern: List[str]) -> Dict[str, Any]:
        """Simulate adaptive cache (combines LRU and LFU)"""
        cache = OrderedDict()
        frequency = {}
        recency_weight = 0.7
        frequency_weight = 0.3
        hits = 0
        misses = 0
        
        for i, item in enumerate(access_pattern):
            if item in cache:
                hits += 1
                frequency[item] = frequency.get(item, 0) + 1
                cache.move_to_end(item)
            else:
                misses += 1
                if len(cache) >= self.cache_size:
                    # Calculate scores combining recency and frequency
                    scores = {}
                    cache_list = list(cache.keys())
                    for idx, key in enumerate(cache_list):
                        recency_score = idx / len(cache_list)  # 0 = oldest, 1 = newest
                        freq_score = frequency.get(key, 1) / max(frequency.values())
                        scores[key] = (recency_weight * recency_score + 
                                     frequency_weight * freq_score)
                    
                    # Evict lowest score
                    min_score_item = min(scores.keys(), key=lambda k: scores[k])
                    del cache[min_score_item]
                    if min_score_item in frequency:
                        del frequency[min_score_item]
                
                cache[item] = True
                frequency[item] = 1
        
        hit_rate = hits / (hits + misses)
        return {
            "strategy": "adaptive",
            "hits": hits,
            "misses": misses,
            "hit_rate": hit_rate,
            "cache_size": len(cache)
        }
    
    async def optimize(self) -> Dict[str, Any]:
        """Run cache optimization simulation"""
        logger.info("Starting n8n cache eviction optimization")
        logger.info(f"Cache size: {self.cache_size}")
        logger.info(f"Testing strategies: {self.strategies}")
        
        # Generate access pattern
        access_pattern = self.generate_access_pattern(10000)
        logger.info(f"Generated {len(access_pattern)} requests")
        
        start_time = time.time()
        
        # Test each strategy
        for strategy in self.strategies:
            result = {}  # Initialize result
            if strategy == "lru":
                result = self.simulate_lru(access_pattern)
            elif strategy == "lfu":
                result = self.simulate_lfu(access_pattern)
            elif strategy == "fifo":
                result = self.simulate_fifo(access_pattern)
            elif strategy == "adaptive":
                result = self.simulate_adaptive(access_pattern)
            
            self.results[strategy] = result
            logger.info(f"{strategy.upper()}: Hit rate = {result['hit_rate']:.1%}")
        
        # Find best strategy
        best_strategy = max(self.results.keys(), 
                          key=lambda s: self.results[s]["hit_rate"])
        
        total_time = time.time() - start_time
        
        return {
            "optimization_time_seconds": total_time,
            "strategies_tested": self.strategies,
            "best_strategy": best_strategy,
            "best_hit_rate": self.results[best_strategy]["hit_rate"],
            "all_results": self.results,
            "cache_size": self.cache_size,
            "requests_simulated": len(access_pattern)
        }

async def run_optimization():
    """Run the optimization process"""
    print("💾 n8n Cache Eviction Optimization")
    print("=" * 50)
    
    # Test different cache sizes
    cache_sizes = [500, 1000, 2000, 5000]
    all_results = {}
    
    for cache_size in cache_sizes:
        print(f"\n🔍 Testing cache size: {cache_size}")
        simulator = CacheSimulator(cache_size)
        results = await simulator.optimize()
        all_results[cache_size] = results
        
        print(f"Best strategy: {results['best_strategy'].upper()}")
        print(f"Best hit rate: {results['best_hit_rate']:.1%}")
    
    # Find optimal configuration
    best_config = max(all_results.items(), 
                     key=lambda x: x[1]["best_hit_rate"])
    optimal_cache_size = best_config[0]
    optimal_results = best_config[1]
    
    print("\n" + "=" * 50)
    print("📊 Optimization Results")
    print("=" * 50)
    
    print("\n✅ Optimal Configuration:")
    print(f"   Cache Size: {optimal_cache_size}")
    print(f"   Strategy: {optimal_results['best_strategy'].upper()}")
    print(f"   Hit Rate: {optimal_results['best_hit_rate']:.1%} {'✅' if optimal_results['best_hit_rate'] > 0.85 else '❌'}")
    
    # Show all results
    print("\n📊 Hit Rates by Cache Size and Strategy:")
    for cache_size, results in sorted(all_results.items()):
        print(f"\nCache Size {cache_size}:")
        for strategy, metrics in results["all_results"].items():
            hit_rate = metrics["hit_rate"]
            print(f"   {strategy.upper()}: {hit_rate:.1%} {'✅' if hit_rate > 0.85 else ''}")
    
    # Save results
    report = {
        "timestamp": datetime.now().isoformat(),
        "optimization_results": all_results,
        "recommendation": {
            "optimal_cache_size": optimal_cache_size,
            "optimal_strategy": optimal_results["best_strategy"],
            "expected_hit_rate": optimal_results["best_hit_rate"],
            "implementation": f"Use {optimal_results['best_strategy'].upper()} with cache size {optimal_cache_size}"
        }
    }
    
    with open("PHASE_4_N8N_CACHE_OPTIMIZATION.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\nDetailed results saved to: PHASE_4_N8N_CACHE_OPTIMIZATION.json")
    
    return optimal_results["best_hit_rate"] > 0.85

if __name__ == "__main__":
    success = asyncio.run(run_optimization())
    exit(0 if success else 1) 