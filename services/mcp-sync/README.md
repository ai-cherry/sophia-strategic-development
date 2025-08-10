# MCP-Notion Sync Service for Sophia

## Overview
This service provides intelligent knowledge synchronization between local development, GitHub, Notion, and Lambda Labs compute infrastructure for the Sophia Strategic Development project.

## Architecture

```
Local Development (Mac)
    ↓
GitHub Repository (Source of Truth)
    ↓
Lambda Labs (GPU Compute + Processing)
    ↓
Notion (Knowledge Base UI)
```

## Components

### 1. Content Deduplication Engine
- Prevents information bloat
- Uses content hashing and semantic similarity
- Maintains version history

### 2. Lambda Labs Integration
- Leverages GPU for embeddings generation
- Semantic search and similarity computation
- Real-time content processing

### 3. Notion Sync
- Bi-directional sync with conflict resolution
- Intelligent updates (not duplicates)
- Workspace organization

## Setup

### Environment Variables Required:
```bash
# Lambda Labs
LAMBDA_CLOUD_API_KEY=your_key
LAMBDA_API_CLOUD_ENDPOINT=https://cloud.lambda.ai/api/v1

# GitHub
GITHUB_PAT=your_pat
GITHUB_USERNAME=your_username

# Notion
NOTION_API_KEY=your_notion_key
NOTION_WORKSPACE_ID=your_workspace_id
```

### Installation:
```bash
cd services/mcp-sync
pip install -r requirements.txt
python setup.py
```

## Usage

### Start sync service:
```bash
python sync_manager.py
```

### Manual sync:
```bash
python sync_manager.py --sync-now
```

### Check for duplicates:
```bash
python dedup_engine.py --check-duplicates
```

## Integration with Sophia

This service integrates with Sophia's main AI system by:
1. Providing clean, deduplicated knowledge base
2. Maintaining context across development sessions
3. Enabling GPU-accelerated semantic search
4. Syncing insights back to Notion for review

## Protection Status

This branch is protected and requires:
- Review before merge
- All tests passing
- No merge conflicts with main

## Future Enhancements

- [ ] Real-time collaboration features
- [ ] Advanced conflict resolution UI
- [ ] Multi-modal content support (images, diagrams)
- [ ] Automated knowledge graph generation
