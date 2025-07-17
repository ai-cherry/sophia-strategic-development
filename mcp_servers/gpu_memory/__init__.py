"""
GPU Memory MCP Server - Tier 0 of the Hybrid Memory Architecture

This module provides GPU-accelerated memory operations including:
- Ultra-fast embedding generation (<10ms)
- GPU memory pooling and management
- CUDA-accelerated operations
- Direct GPU memory access for Lambda Labs infrastructure
"""

from .gpu_memory_server import GPUMemoryMCPServer

__all__ = ['GPUMemoryMCPServer']
