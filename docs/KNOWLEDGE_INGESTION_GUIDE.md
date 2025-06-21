# Sophia AI Knowledge Ingestion & Curation Guide

## Overview

The Sophia AI Knowledge Ingestion & Curation System provides a comprehensive framework for building and maintaining Pay Ready's intelligent knowledge base. This system combines manual document management, automated insight discovery from Gong calls, and interactive curation tools to ensure the knowledge base remains accurate, relevant, and continuously improving.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Knowledge Admin Portal                         │
├─────────────────┬──────────────────┬────────────────────────────┤
│ Document Upload │ Discovery Queue  │   Curation Chat           │
│   & Management  │ (Proactive AI)   │ (Interactive Refinement)  │
└────────┬────────┴────────┬─────────┴──────────┬─────────────────┘
         │                 │                     │
         ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend Services                              │
├─────────────────┬──────────────────┬────────────────────────────┤
│   Ingestion     │ Insight Extract  │   Knowledge Manager       │
│   Pipeline      │     Agent        │                           │
└────────┬────────┴────────┬─────────┴──────────┬─────────────────┘
         │                 │                     │
         ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Storage Layer                            │
├─────────────────┬──────────────────┬────────────────────────────┤
│ Pinecone Vector │ Metadata Store   │   PostgreSQL DB           │
│     Database    │                  │                           │
└─────────────────┴──────────────────┴────────────────────────────┘
```

## Key Features

### 1. Multi-Format Document Upload
- **Supported Formats**: PDF, Word (DOC/DOCX), Excel (XLS/XLSX), Text (TXT), CSV, Markdown (MD)
- **Drag-and-drop interface** for easy bulk uploads
- **Automatic text extraction** and parsing
- **Metadata tagging** for categorization

### 2. Proactive Discovery Queue
- **Automated Gong transcript analysis** using AI
- **Intelligent insight extraction** for:
  - New competitors
  - Product gaps and limitations
  - Unexpected use cases
  - Pricing objections
  - Feature requests
  - Integration needs
  - Security concerns
- **Human-in-the-loop validation** before adding to knowledge base
- **Confidence scoring** for each discovered insight

### 3. Knowledge Curation Chat
- **Natural language interface** for testing knowledge base
- **Source citation** for every response
- **Interactive feedback mechanism**:
  - Thumbs up for correct information
  - Thumbs down with correction capability
- **Immediate knowledge base updates** based on feedback

## Getting Started

### Prerequisites

1. **Environment Variables**:
   ```bash
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_ENVIRONMENT=your_environment
   OPENAI_API_KEY=your_openai_key
   GONG_API_KEY=your_gong_key
   ```

2. **Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Initial Setup

1. **Initialize the Knowledge Base**:
   ```bash
   python scripts/test_knowledge_ingestion.py
   ```

2. **Start the Backend Services**:
   ```bash
   python backend/main.py
   ```

3. **Launch the Knowledge Admin Portal**:
   ```bash
   cd frontend/knowledge-admin
   npm install
   npm run dev
   ```

## Usage Guide

### Manual Document Upload

1. Navigate to the Knowledge Admin Portal
2. Click "Upload Files" button
3. Select or drag-and-drop your documents
4. Choose appropriate category and add tags
5. Click "Upload" to process

### Managing Proactive Insights

1. **Automatic Discovery**:
   - The system continuously monitors new Gong calls
   - AI analyzes transcripts for novel information
   - Insights appear in the Discovery Queue

2. **Review Process**:
   - Click on the Discovery Queue tab
   - Review each pending insight
   - Choose an action:
     - **Approve**: Add to knowledge base as-is
     - **Approve with Edit**: Modify before adding
     - **Reject**: Discard the insight
     - **Ask Later**: Defer decision

3. **Batch Processing**:
   ```python
   # Analyze last 24 hours of calls
   POST /api/knowledge/insights/batch-analyze
   {
     "hours_back": 24
   }
   ```

### Using the Curation Chat

1. Navigate to the Curation Chat tab
2. Ask natural language questions about your knowledge base
3. Review Sophia's responses and sources
4. Provide feedback:
   - If correct: Click thumbs up
   - If incorrect: Click thumbs down and provide correction

### API Integration

#### Upload Documents Programmatically
```python
import requests

files = [
    ('files', open('pricing_guide.pdf', 'rb')),
    ('files', open('product_specs.docx', 'rb'))
]
data = {
    'category': 'products_services',
    'tags': 'pricing,products,2024'
}

response = requests.post(
    'http://localhost:8000/api/knowledge/documents/upload',
    files=files,
    data=data
)
```

#### Query the Knowledge Base
```python
response = requests.post(
    'http://localhost:8000/api/knowledge/curation/chat',
    json={'query': 'What is our Enterprise pricing?'}
)

print(response.json())
# {
#   "content": "The Enterprise Tier is priced at $60,000 per year...",
#   "source": "product_pricing.txt",
#   "confidence": 0.95,
#   "needsFeedback": true
# }
```

## Best Practices

### Document Organization

1. **Use Clear Naming Conventions**:
   - `company_mission_2024.pdf`
   - `product_pricing_q1_2024.xlsx`
   - `competitor_analysis_entrata.docx`

2. **Categorize Appropriately**:
   - `company_core`: Mission, values, culture
   - `products_services`: Features, capabilities
   - `pricing`: Pricing tiers, discounts
   - `competitive_intel`: Competitor analysis
   - `operations`: Processes, procedures

3. **Tag Comprehensively**:
   - Include temporal tags: `2024`, `q1`
   - Include topic tags: `pricing`, `features`
   - Include audience tags: `sales`, `support`

### Proactive Discovery Management

1. **Review Insights Promptly**: Check Discovery Queue daily
2. **Validate Context**: Always review the source call before approving
3. **Edit for Clarity**: Refine insights to be clear and actionable
4. **Track Patterns**: Look for recurring themes across multiple calls

### Knowledge Curation

1. **Test Regularly**: Use the chat to verify critical information
2. **Update Promptly**: Correct outdated information immediately
3. **Monitor Confidence**: Pay attention to low-confidence responses
4. **Document Edge Cases**: Add clarifications for ambiguous topics

## Integration with CEO Dashboard

The knowledge base directly powers the CEO Dashboard's Strategic Chat:

```python
# CEO Dashboard query flow
User: "What are the risks for QuantumLeap Solutions?"

1. Query ClientHealthAgent for real-time data
2. Query Knowledge Base for competitor intel
3. Synthesize comprehensive response
4. Present with actionable insights
```

## Troubleshooting

### Common Issues

1. **Upload Failures**:
   - Check file size (max 10MB per file)
   - Verify file format is supported
   - Ensure proper permissions

2. **Slow Queries**:
   - Check Pinecone index status
   - Verify API keys are valid
   - Monitor rate limits

3. **Missing Insights**:
   - Verify Gong integration is active
   - Check webhook configuration
   - Review agent logs

### Debug Commands

```bash
# Test knowledge base connection
python -m backend.knowledge_base.vector_store test

# Check pending insights
curl http://localhost:8000/api/knowledge/insights/pending

# Verify document count
curl http://localhost:8000/api/knowledge/analytics/stats
```

## Security Considerations

1. **Access Control**: Implement role-based access for sensitive documents
2. **Data Encryption**: All documents encrypted at rest
3. **Audit Logging**: Track all changes and access
4. **API Authentication**: Secure all endpoints with proper auth

## Future Enhancements

1. **Automated Knowledge Extraction** from:
   - Email threads
   - Slack conversations
   - Support tickets

2. **Advanced Analytics**:
   - Knowledge gap analysis
   - Usage patterns
   - ROI tracking

3. **AI-Powered Suggestions**:
   - Proactive document recommendations
   - Auto-categorization
   - Duplicate detection

## Support

For assistance or questions:
- Technical Issues: sophia-tech@payready.com
- Feature Requests: Submit via Linear (SOPH project)
- Documentation: See `/docs` directory
