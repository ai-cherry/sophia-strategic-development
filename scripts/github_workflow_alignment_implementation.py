#!/usr/bin/env python3
"""Qdrant vector database"""
    aligner = GitHubWorkflowAligner()
    success = aligner.run_complete_alignment()
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main() 