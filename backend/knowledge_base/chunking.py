"""
Text Chunking for the Knowledge Base
Splits large text documents into smaller, semantically coherent chunks.
"""
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Chunk:
    """Represents a single chunk of text with its metadata."""
    content: str
    metadata: Dict[str, Any]
    
class TextChunker:
    """
    A class to split text into chunks using a recursive character-based method.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: List[str] = None):
        """
        Initializes the TextChunker.
        
        Args:
            chunk_size: The target size for each chunk (in characters).
            chunk_overlap: The number of characters to overlap between chunks.
            separators: A list of separators to split the text on, in order of preference.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
        
    def split_text(self, text: str) -> List[str]:
        """
        Splits a large text into smaller chunks based on the configured separators.
        
        Args:
            text: The input text to be chunked.
            
        Returns:
            A list of text chunks.
        """
        final_chunks = []
        
        # Start with the largest separator
        separator = self.separators[0]
        splits = text.split(separator)
        
        # Process these splits
        current_chunk = ""
        for i, split in enumerate(splits):
            if not split:
                continue
            
            # If adding the next split doesn't exceed the chunk size, add it
            if len(current_chunk) + len(split) + len(separator) <= self.chunk_size:
                current_chunk += separator + split
            else:
                # If the current chunk is not empty, add it to the list
                if current_chunk:
                    final_chunks.append(current_chunk.strip())
                
                # Start a new chunk, potentially with overlap from the previous
                # This simple implementation doesn't handle overlap elegantly across splits.
                # For a more robust solution, we'd recursively split larger chunks.
                current_chunk = split
                
        # Add the last remaining chunk
        if current_chunk:
            final_chunks.append(current_chunk.strip())
            
        # Refine chunks to ensure they are within size limits (a more robust way)
        return self._refine_chunks(final_chunks)

    def _refine_chunks(self, initial_chunks: List[str]) -> List[str]:
        """
        Recursively splits chunks that are too large.
        """
        final_chunks = []
        for chunk in initial_chunks:
            if len(chunk) <= self.chunk_size:
                final_chunks.append(chunk)
            else:
                # This is a simplified recursive split. A library like LangChain's
                # TextSplitter would be more robust here.
                # We split the oversized chunk by the next separator.
                
                # For this implementation, we'll just split by length.
                for i in range(0, len(chunk), self.chunk_size - self.chunk_overlap):
                    final_chunks.append(chunk[i:i + self.chunk_size])
        
        return final_chunks

    def create_chunks(self, text: str, document_metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Creates Chunk objects from a text, adding document-level metadata to each.
        
        Args:
            text: The input text.
            document_metadata: Metadata associated with the entire document.
            
        Returns:
            A list of Chunk objects.
        """
        text_chunks = self.split_text(text)
        chunks = []
        for i, chunk_content in enumerate(text_chunks):
            chunk_metadata = document_metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "chunk_length_chars": len(chunk_content)
            })
            chunks.append(Chunk(content=chunk_content, metadata=chunk_metadata))
            
        logger.info(f"Split text into {len(chunks)} chunks for document: {document_metadata.get('file_name')}")
        return chunks

async def main():
    """A simple main function to test the chunker."""
    test_text = """This is the first paragraph. It introduces the topic.

This is the second paragraph. It provides more details and can be quite long. In fact, it might be long enough to be split into multiple chunks if the chunk size is small. Let's see what happens. We will keep writing to make sure it exceeds a reasonable chunk size. The goal of chunking is to create semantically coherent pieces of text that can be vectorized and searched effectively.

The third paragraph is here. It concludes the main points.
This is still the third paragraph.
"""
    
    document_metadata = {
        "file_name": "test_document.txt",
        "source": "manual_test"
    }
    
    # Test with a small chunk size to see splitting in action
    chunker = TextChunker(chunk_size=150, chunk_overlap=30)
    chunks = chunker.create_chunks(test_text, document_metadata)
    
    print(f"--- Created {len(chunks)} Chunks ---\n")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}:")
        print(f"Metadata: {chunk.metadata}")
        print(f"Content: '{chunk.content}'")
        print("-" * 20)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 