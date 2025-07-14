"""
Document Chunking Service for Sophia AI Memory Ecosystem

Implements advanced chunking strategies for optimal document processing
and context preservation in the RAG pipeline.
"""

import re
import hashlib
import logging
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from backend.services.unified_memory_service_v2 import get_unified_memory_service
from backend.services.redis_helper import RedisHelper
from shared.utils.monitoring import log_execution_time

logger = logging.getLogger(__name__)


class ChunkingStrategy(Enum):
    """Available chunking strategies"""

    SEMANTIC = "semantic"
    HIERARCHICAL = "hierarchical"
    SLIDING_WINDOW = "sliding_window"
    CONTEXT_AWARE = "context_aware"
    HYBRID = "hybrid"


@dataclass
class DocumentChunk:
    """Represents a document chunk with metadata"""

    chunk_id: str
    document_id: str
    content: str
    sequence: int
    strategy: ChunkingStrategy
    metadata: Dict[str, Any] = field(default_factory=dict)
    embeddings: Optional[List[float]] = None
    quality_score: float = 0.0
    parent_chunk_id: Optional[str] = None
    child_chunk_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ChunkingConfig:
    """Configuration for chunking strategies"""

    # Sliding window config
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Semantic chunking config
    similarity_threshold: float = 0.7
    min_semantic_chunk_size: int = 100
    max_semantic_chunk_size: int = 1500

    # Hierarchical config
    preserve_headers: bool = True
    min_section_size: int = 200
    max_hierarchy_depth: int = 5

    # Context-aware config
    preserve_entities: bool = True
    preserve_references: bool = True
    context_window: int = 100

    # Quality thresholds
    min_coherence_score: float = 0.8
    min_information_density: float = 0.6


class DocumentChunkingService:
    """Advanced document chunking service with multiple strategies"""

    def __init__(self, config: Optional[ChunkingConfig] = None):
        self.config = config or ChunkingConfig()
        self.memory_service = get_unified_memory_service()
        self.redis_helper = RedisHelper()
        self.cache_ttl = 3600  # 1 hour cache for chunks

    @log_execution_time
    async def chunk_document(
        self,
        document: str,
        document_id: str,
        strategy: ChunkingStrategy = ChunkingStrategy.HYBRID,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """
        Chunk a document using the specified strategy

        Args:
            document: The document text to chunk
            document_id: Unique identifier for the document
            strategy: The chunking strategy to use
            metadata: Additional metadata for the document

        Returns:
            List of document chunks
        """
        # Check cache first
        cache_key = f"chunks:{document_id}:{strategy.value}"
        cached_chunks = await self.redis_helper.get_cached_search_results(cache_key)
        if cached_chunks:
            return [DocumentChunk(**chunk) for chunk in cached_chunks]

        # Apply chunking strategy
        if strategy == ChunkingStrategy.SLIDING_WINDOW:
            chunks = await self._sliding_window_chunk(document, document_id, metadata)
        elif strategy == ChunkingStrategy.SEMANTIC:
            chunks = await self._semantic_chunk(document, document_id, metadata)
        elif strategy == ChunkingStrategy.HIERARCHICAL:
            chunks = await self._hierarchical_chunk(document, document_id, metadata)
        elif strategy == ChunkingStrategy.CONTEXT_AWARE:
            chunks = await self._context_aware_chunk(document, document_id, metadata)
        elif strategy == ChunkingStrategy.HYBRID:
            chunks = await self._hybrid_chunk(document, document_id, metadata)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")

        # Calculate quality scores
        for chunk in chunks:
            chunk.quality_score = await self._calculate_chunk_quality(chunk)

        # Cache the results
        cache_data = [
            {
                "chunk_id": c.chunk_id,
                "document_id": c.document_id,
                "content": c.content,
                "sequence": c.sequence,
                "strategy": c.strategy.value,
                "metadata": c.metadata,
                "quality_score": c.quality_score,
                "parent_chunk_id": c.parent_chunk_id,
                "child_chunk_ids": c.child_chunk_ids,
                "created_at": c.created_at.isoformat(),
            }
            for c in chunks
        ]
        await self.redis_helper.cache_search_results(
            cache_key, cache_data, self.cache_ttl
        )

        return chunks

    async def _sliding_window_chunk(
        self, document: str, document_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """Implement sliding window chunking with overlap"""
        chunks = []
        sentences = self._split_into_sentences(document)

        current_chunk = []
        current_size = 0
        sequence = 0

        for i, sentence in enumerate(sentences):
            sentence_size = len(sentence.split())

            if current_size + sentence_size > self.config.chunk_size and current_chunk:
                # Create chunk
                chunk_content = " ".join(current_chunk)
                chunk_id = self._generate_chunk_id(document_id, sequence, chunk_content)

                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        content=chunk_content,
                        sequence=sequence,
                        strategy=ChunkingStrategy.SLIDING_WINDOW,
                        metadata={
                            **(metadata or {}),
                            "start_sentence": i - len(current_chunk),
                            "end_sentence": i - 1,
                            "word_count": current_size,
                        },
                    )
                )

                # Create overlap
                overlap_sentences = int(
                    self.config.chunk_overlap / 20
                )  # Approx words per sentence
                current_chunk = (
                    current_chunk[-overlap_sentences:] if overlap_sentences > 0 else []
                )
                current_size = sum(len(s.split()) for s in current_chunk)
                sequence += 1

            current_chunk.append(sentence)
            current_size += sentence_size

        # Add final chunk
        if current_chunk:
            chunk_content = " ".join(current_chunk)
            chunk_id = self._generate_chunk_id(document_id, sequence, chunk_content)

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    content=chunk_content,
                    sequence=sequence,
                    strategy=ChunkingStrategy.SLIDING_WINDOW,
                    metadata={
                        **(metadata or {}),
                        "start_sentence": len(sentences) - len(current_chunk),
                        "end_sentence": len(sentences) - 1,
                        "word_count": current_size,
                    },
                )
            )

        return chunks

    async def _semantic_chunk(
        self, document: str, document_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """Implement semantic chunking based on topic coherence"""
        chunks = []
        sentences = self._split_into_sentences(document)

        if not sentences:
            return chunks

        # Generate embeddings for each sentence
        sentence_embeddings = []
        for sentence in sentences:
            embedding = await self.memory_service.generate_embedding(sentence)
            sentence_embeddings.append(embedding)

        # Find semantic boundaries
        boundaries = [0]
        current_chunk_start = 0

        for i in range(1, len(sentences)):
            # Calculate similarity with previous sentences in current chunk
            if i - current_chunk_start >= self.config.min_semantic_chunk_size:
                # Calculate average similarity within current chunk
                chunk_embeddings = sentence_embeddings[current_chunk_start:i]
                avg_embedding = np.mean(chunk_embeddings, axis=0)

                # Check similarity with next sentence
                similarity = cosine_similarity(
                    [avg_embedding], [sentence_embeddings[i]]
                )[0][0]

                # If similarity is below threshold, create boundary
                if similarity < self.config.similarity_threshold:
                    boundaries.append(i)
                    current_chunk_start = i

            # Force boundary at max chunk size
            if i - current_chunk_start >= self.config.max_semantic_chunk_size:
                boundaries.append(i)
                current_chunk_start = i

        boundaries.append(len(sentences))

        # Create chunks from boundaries
        sequence = 0
        for i in range(len(boundaries) - 1):
            start_idx = boundaries[i]
            end_idx = boundaries[i + 1]

            chunk_sentences = sentences[start_idx:end_idx]
            chunk_content = " ".join(chunk_sentences)
            chunk_id = self._generate_chunk_id(document_id, sequence, chunk_content)

            # Calculate chunk embedding as average of sentence embeddings
            chunk_embeddings = sentence_embeddings[start_idx:end_idx]
            avg_embedding = np.mean(chunk_embeddings, axis=0).tolist()

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    content=chunk_content,
                    sequence=sequence,
                    strategy=ChunkingStrategy.SEMANTIC,
                    metadata={
                        **(metadata or {}),
                        "sentence_count": len(chunk_sentences),
                        "semantic_coherence": self._calculate_coherence(
                            chunk_embeddings
                        ),
                    },
                    embeddings=avg_embedding,
                )
            )

            sequence += 1

        return chunks

    async def _hierarchical_chunk(
        self, document: str, document_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """Implement hierarchical chunking preserving document structure"""
        chunks = []

        # Detect document structure (headers, sections, etc.)
        sections = self._detect_document_structure(document)

        sequence = 0
        chunk_hierarchy = {}

        for section in sections:
            # Create chunk for this section
            chunk_id = self._generate_chunk_id(
                document_id, sequence, section["content"]
            )

            parent_id = None
            if section["level"] > 0 and section["parent_idx"] is not None:
                parent_id = chunk_hierarchy.get(section["parent_idx"])

            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                content=section["content"],
                sequence=sequence,
                strategy=ChunkingStrategy.HIERARCHICAL,
                metadata={
                    **(metadata or {}),
                    "section_title": section["title"],
                    "hierarchy_level": section["level"],
                    "section_type": section["type"],
                },
                parent_chunk_id=parent_id,
            )

            # Update parent's child references
            if parent_id:
                for existing_chunk in chunks:
                    if existing_chunk.chunk_id == parent_id:
                        existing_chunk.child_chunk_ids.append(chunk_id)
                        break

            chunks.append(chunk)
            chunk_hierarchy[sequence] = chunk_id
            sequence += 1

        return chunks

    async def _context_aware_chunk(
        self, document: str, document_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """Implement context-aware chunking preserving entities and references"""

        # Extract entities and references
        entities = self._extract_entities(document)
        references = self._extract_references(document)

        # Use sliding window as base
        base_chunks = await self._sliding_window_chunk(document, document_id, metadata)

        # Enhance chunks with context
        for chunk in base_chunks:
            # Find entities in this chunk
            chunk_entities = []
            for entity in entities:
                if entity["text"] in chunk.content:
                    chunk_entities.append(entity)

            # Find references that need context
            chunk_references = []
            for ref in references:
                if ref["reference"] in chunk.content:
                    # Check if the referenced content is in the chunk
                    if ref["target"] not in chunk.content:
                        # Add context window around reference
                        context_start = max(
                            0, ref["position"] - self.config.context_window
                        )
                        context_end = min(
                            len(document), ref["position"] + self.config.context_window
                        )
                        context = document[context_start:context_end]
                        chunk_references.append(
                            {"reference": ref["reference"], "context": context}
                        )

            # Update chunk metadata
            chunk.metadata.update(
                {
                    "entities": chunk_entities,
                    "references": chunk_references,
                    "has_incomplete_context": len(chunk_references) > 0,
                }
            )

        return base_chunks

    async def _hybrid_chunk(
        self, document: str, document_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """Implement hybrid chunking combining multiple strategies"""
        # Start with hierarchical structure
        hierarchical_chunks = await self._hierarchical_chunk(
            document, document_id, metadata
        )

        # For each large hierarchical chunk, apply semantic chunking
        final_chunks = []

        for h_chunk in hierarchical_chunks:
            if len(h_chunk.content.split()) > self.config.chunk_size:
                # Apply semantic chunking to large sections
                semantic_chunks = await self._semantic_chunk(
                    h_chunk.content,
                    document_id,
                    {
                        **h_chunk.metadata,
                    },
                )

                # Link chunks hierarchically
                for i, s_chunk in enumerate(semantic_chunks):
                    s_chunk.parent_chunk_id = h_chunk.chunk_id
                    s_chunk.metadata["hierarchy_path"] = [
                        h_chunk.metadata.get("section_title", ""),
                        f"Part {i + 1}",
                    ]
                    final_chunks.append(s_chunk)

                h_chunk.child_chunk_ids = [c.chunk_id for c in semantic_chunks]
                final_chunks.append(h_chunk)
            else:
                # Keep small sections as-is
                final_chunks.append(h_chunk)

        # Apply context-aware enhancements
        entities = self._extract_entities(document)
        references = self._extract_references(document)

        for chunk in final_chunks:
            # Add entity and reference information
            chunk_entities = [e for e in entities if e["text"] in chunk.content]
            chunk_references = [
                r for r in references if r["reference"] in chunk.content
            ]

            chunk.metadata.update(
                {"entities": chunk_entities, "references": chunk_references}
            )

        return final_chunks

    async def _calculate_chunk_quality(self, chunk: DocumentChunk) -> float:
        """Calculate quality score for a chunk"""
        scores = []

        # Coherence score (based on sentence similarity if available)
        if hasattr(self, "_calculate_coherence"):
            coherence_score = self._calculate_coherence_from_text(chunk.content)
            scores.append(coherence_score)

        # Information density (ratio of unique words to total words)
        words = chunk.content.lower().split()
        if words:
            unique_ratio = len(set(words)) / len(words)
            scores.append(unique_ratio)

        # Completeness (check for incomplete sentences)
        completeness_score = self._calculate_completeness(chunk.content)
        scores.append(completeness_score)

        # Size appropriateness
        word_count = len(words)
        if self.config.chunk_size * 0.5 <= word_count <= self.config.chunk_size * 1.5:
            size_score = 1.0
        else:
            size_score = 0.5
        scores.append(size_score)

        # Calculate weighted average
        return sum(scores) / len(scores) if scores else 0.0

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Enhanced sentence splitting with abbreviation handling
        text = re.sub(r"\s+", " ", text.strip())

        # Handle common abbreviations
        text = re.sub(r"\b(Mr|Mrs|Dr|Ms|Prof|Sr|Jr)\.\s*", r"\1<DOT> ", text)
        text = re.sub(r"\b(Inc|Ltd|Corp|Co)\.\s*", r"\1<DOT> ", text)
        text = re.sub(
            r"\b([A-Z])\.\s*", r"\1<DOT> ", text
        )  # Single letter abbreviations

        # Split on sentence boundaries
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)

        # Restore dots
        sentences = [s.replace("<DOT>", ".") for s in sentences]

        return [s.strip() for s in sentences if s.strip()]

    def _detect_document_structure(self, document: str) -> List[Dict[str, Any]]:
        """Detect hierarchical structure in document"""
        lines = document.split("\n")
        sections = []
        current_section = []

        # Patterns for headers
        header_patterns = [
            (r"^#{1,6}\s+(.+)$", "markdown"),
            (r"^([A-Z][^.!?]*):?\s*$", "title"),
            (r"^\d+\.\s+(.+)$", "numbered"),
            (r"^[A-Z]\.\s+(.+)$", "lettered"),
        ]

        for i, line in enumerate(lines):
            is_header = False

            for pattern, header_type in header_patterns:
                match = re.match(pattern, line)
                if match:
                    # Save current section
                    if current_section:
                        content = "\n".join(current_section).strip()
                        if content:
                            sections.append(
                                {
                                    "content": content,
                                    "title": "",
                                    "level": 0,
                                    "type": "content",
                                    "parent_idx": None,
                                }
                            )

                    # Start new section
                    header_text = match.group(1) if match.groups() else line
                    level = line.count("#") if header_type == "markdown" else 1

                    sections.append(
                        {
                            "content": line,
                            "title": header_text,
                            "level": level,
                            "type": header_type,
                            "parent_idx": self._find_parent_section(sections, level),
                        }
                    )

                    current_section = []
                    is_header = True
                    break

            if not is_header:
                current_section.append(line)

        # Add final section
        if current_section:
            content = "\n".join(current_section).strip()
            if content:
                sections.append(
                    {
                        "content": content,
                        "title": "",
                        "level": 0,
                        "type": "content",
                        "parent_idx": len(sections) - 1 if sections else None,
                    }
                )

        return sections

    def _find_parent_section(self, sections: List[Dict], level: int) -> Optional[int]:
        """Find parent section index for hierarchical structure"""
        for i in range(len(sections) - 1, -1, -1):
            if sections[i]["level"] < level:
                return i
        return None

    def _extract_entities(self, document: str) -> List[Dict[str, Any]]:
        """Extract named entities from document"""
        entities = []

        # Simple pattern-based entity extraction
        # In production, use spaCy or similar NLP library

        # Email patterns
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        for match in re.finditer(email_pattern, document):
            entities.append(
                {"text": match.group(), "type": "email", "position": match.start()}
            )

        # URL patterns
        url_pattern = r"https?://[^\s]+"
        for match in re.finditer(url_pattern, document):
            entities.append(
                {"text": match.group(), "type": "url", "position": match.start()}
            )

        # Simple name pattern (capitalized words)
        name_pattern = r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"
        for match in re.finditer(name_pattern, document):
            entities.append(
                {"text": match.group(), "type": "person", "position": match.start()}
            )

        return entities

    def _extract_references(self, document: str) -> List[Dict[str, Any]]:
        """Extract references and cross-references from document"""
        references = []

        # Common reference patterns
        ref_patterns = [
            (r"see (section|chapter|page) (\d+)", "section_ref"),
            (r"as mentioned (above|below|earlier)", "relative_ref"),
            (r"refer to (.+?) for", "external_ref"),
            (r"\[(\d+)\]", "citation"),
            (r"Figure (\d+)", "figure_ref"),
            (r"Table (\d+)", "table_ref"),
        ]

        for pattern, ref_type in ref_patterns:
            for match in re.finditer(pattern, document, re.IGNORECASE):
                references.append(
                    {
                        "reference": match.group(),
                        "type": ref_type,
                        "position": match.start(),
                        "target": match.group(1) if match.groups() else None,
                    }
                )

        return references

    def _calculate_coherence(self, embeddings: List[List[float]]) -> float:
        """Calculate coherence score from embeddings"""
        if len(embeddings) < 2:
            return 1.0

        # Calculate average pairwise similarity
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                similarities.append(sim)

        return np.mean(similarities) if similarities else 1.0

    def _calculate_coherence_from_text(self, text: str) -> float:
        """Calculate coherence score from text (simplified version)"""
        sentences = self._split_into_sentences(text)
        if len(sentences) < 2:
            return 1.0

        # Simple coherence: check for connecting words
        connecting_words = [
            "however",
            "therefore",
            "moreover",
            "furthermore",
            "additionally",
            "consequently",
            "thus",
            "hence",
        ]

        connection_count = sum(1 for word in connecting_words if word in text.lower())

        # Normalize by number of sentences
        coherence = min(1.0, connection_count / (len(sentences) - 1))

        return 0.7 + (0.3 * coherence)  # Base coherence + connection bonus

    def _calculate_completeness(self, text: str) -> float:
        """Calculate completeness score for text"""
        # Check for incomplete sentences
        sentences = self._split_into_sentences(text)
        if not sentences:
            return 0.0

        complete_sentences = 0
        for sentence in sentences:
            # Simple check: does it end with proper punctuation?
            if sentence.rstrip().endswith((".", "!", "?")):
                complete_sentences += 1

        return complete_sentences / len(sentences)

    def _generate_chunk_id(self, document_id: str, sequence: int, content: str) -> str:
        """Generate unique chunk ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{document_id}_chunk_{sequence}_{content_hash}"
