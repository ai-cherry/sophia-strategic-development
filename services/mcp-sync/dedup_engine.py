#!/usr/bin/env python3
"""
Content Deduplication Engine for Sophia
Prevents information bloat through intelligent content management
"""

import hashlib
import json
import re
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher
import numpy as np
from datetime import datetime, timedelta

class DeduplicationEngine:
    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize deduplication engine
        
        Args:
            similarity_threshold: Minimum similarity to consider content duplicate (0-1)
        """
        self.similarity_threshold = similarity_threshold
        self.content_index = {}  # hash -> content mapping
        self.metadata_index = {}  # hash -> metadata mapping
        
    def generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content"""
        normalized = self.normalize_content(content)
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def normalize_content(self, content: str) -> str:
        """Normalize content for comparison"""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        # Convert to lowercase for comparison
        content = content.lower().strip()
        # Remove timestamps and dates for comparison
        content = re.sub(r'\d{4}-\d{2}-\d{2}', '', content)
        content = re.sub(r'\d{2}:\d{2}:\d{2}', '', content)
        return content
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using SequenceMatcher"""
        norm1 = self.normalize_content(text1)
        norm2 = self.normalize_content(text2)
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def find_duplicates(self, new_content: str, existing_contents: List[Dict]) -> List[Tuple[str, float]]:
        """
        Find potential duplicates of new content
        
        Returns:
            List of (content_id, similarity_score) tuples
        """
        duplicates = []
        new_hash = self.generate_content_hash(new_content)
        
        for existing in existing_contents:
            existing_hash = existing.get('hash', self.generate_content_hash(existing['content']))
            
            # Quick check: exact hash match
            if new_hash == existing_hash:
                duplicates.append((existing['id'], 1.0))
                continue
            
            # Detailed check: content similarity
            similarity = self.calculate_text_similarity(new_content, existing['content'])
            
            if similarity >= self.similarity_threshold:
                duplicates.append((existing['id'], similarity))
        
        return sorted(duplicates, key=lambda x: x[1], reverse=True)
    
    def merge_content(self, content1: str, content2: str, metadata1: Dict = None, metadata2: Dict = None) -> Dict:
        """
        Intelligently merge two similar pieces of content
        """
        # Determine which content is newer/more complete
        len1, len2 = len(content1), len(content2)
        
        # Use longer content as base (usually more complete)
        if len1 >= len2:
            base_content = content1
            additional_content = content2
            base_metadata = metadata1 or {}
        else:
            base_content = content2
            additional_content = content1
            base_metadata = metadata2 or {}
        
        # Find unique sections in additional content
        unique_sections = self.extract_unique_sections(additional_content, base_content)
        
        # Merge unique sections
        if unique_sections:
            merged_content = base_content + "\n\n## Additional Information\n" + "\n".join(unique_sections)
        else:
            merged_content = base_content
        
        # Merge metadata
        merged_metadata = {
            **base_metadata,
            'merged_at': datetime.now().isoformat(),
            'merge_count': base_metadata.get('merge_count', 0) + 1,
            'sources': list(set(base_metadata.get('sources', []) + [metadata1.get('source'), metadata2.get('source')]))
        }
        
        return {
            'content': merged_content,
            'metadata': merged_metadata,
            'hash': self.generate_content_hash(merged_content)
        }
    
    def extract_unique_sections(self, content: str, reference: str, min_length: int = 50) -> List[str]:
        """
        Extract sections from content that don't exist in reference
        """
        unique_sections = []
        
        # Split content into sentences
        sentences = re.split(r'[.!?]\s+', content)
        reference_lower = reference.lower()
        
        current_section = []
        for sentence in sentences:
            sentence_clean = sentence.strip()
            if len(sentence_clean) < 10:
                continue
                
            # Check if sentence exists in reference
            if sentence_clean.lower() not in reference_lower:
                current_section.append(sentence_clean)
            else:
                # Save current section if it's long enough
                if current_section and len(' '.join(current_section)) >= min_length:
                    unique_sections.append(' '.join(current_section) + '.')
                current_section = []
        
        # Don't forget the last section
        if current_section and len(' '.join(current_section)) >= min_length:
            unique_sections.append(' '.join(current_section) + '.')
        
        return unique_sections
    
    def archive_old_content(self, contents: List[Dict], days_threshold: int = 30) -> Tuple[List[Dict], List[Dict]]:
        """
        Separate old content for archiving
        
        Returns:
            (active_content, archived_content)
        """
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        
        active = []
        archived = []
        
        for content in contents:
            last_updated = content.get('metadata', {}).get('last_updated')
            if last_updated:
                update_date = datetime.fromisoformat(last_updated)
                if update_date < threshold_date:
                    archived.append(content)
                else:
                    active.append(content)
            else:
                active.append(content)  # Keep content without dates
        
        return active, archived
    
    def generate_dedup_report(self, contents: List[Dict]) -> Dict:
        """
        Generate a deduplication report for given contents
        """
        total_content = len(contents)
        unique_hashes = set()
        duplicates_found = []
        
        for i, content in enumerate(contents):
            content_hash = self.generate_content_hash(content.get('content', ''))
            
            if content_hash in unique_hashes:
                # Found duplicate
                duplicates_found.append({
                    'index': i,
                    'id': content.get('id'),
                    'hash': content_hash
                })
            else:
                unique_hashes.add(content_hash)
        
        # Calculate potential space savings
        duplicate_count = len(duplicates_found)
        dedup_ratio = (duplicate_count / total_content * 100) if total_content > 0 else 0
        
        report = {
            'total_items': total_content,
            'unique_items': len(unique_hashes),
            'duplicates': duplicate_count,
            'deduplication_ratio': f'{dedup_ratio:.2f}%',
            'duplicate_details': duplicates_found[:10],  # First 10 for brevity
            'recommendation': self.generate_recommendation(dedup_ratio)
        }
        
        return report
    
    def generate_recommendation(self, dedup_ratio: float) -> str:
        """Generate recommendation based on deduplication ratio"""
        if dedup_ratio < 5:
            return "Content is well-managed with minimal duplicates."
        elif dedup_ratio < 15:
            return "Some duplicates found. Consider running periodic deduplication."
        elif dedup_ratio < 30:
            return "Significant duplicates detected. Deduplication recommended."
        else:
            return "High duplicate ratio. Immediate deduplication strongly recommended."

# CLI interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Content Deduplication Engine')
    parser.add_argument('--check-duplicates', action='store_true', help='Check for duplicates in current content')
    parser.add_argument('--threshold', type=float, default=0.8, help='Similarity threshold (0-1)')
    parser.add_argument('--input-file', type=str, help='JSON file with content to check')
    
    args = parser.parse_args()
    
    engine = DeduplicationEngine(similarity_threshold=args.threshold)
    
    if args.check_duplicates and args.input_file:
        with open(args.input_file, 'r') as f:
            contents = json.load(f)
        
        report = engine.generate_dedup_report(contents)
        print(json.dumps(report, indent=2))
