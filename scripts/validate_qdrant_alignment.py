#!/usr/bin/env python3
"""Qdrant vector database"""
    validator = QdrantAlignmentValidator()
    success = validator.run_validation()
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
