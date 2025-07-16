"""
Core Entity Matching Engine
Advanced multi-layer entity resolution with fuzzy matching capabilities
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import re

# Optional fuzzy matching libraries (graceful degradation if not available)
try:
    from fuzzywuzzy import fuzz, process
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    
try:
    import Levenshtein
    LEVENSHTEIN_AVAILABLE = True
except ImportError:
    LEVENSHTEIN_AVAILABLE = False

try:
    from jellyfish import jaro_winkler_similarity, metaphone, double_metaphone
    JELLYFISH_AVAILABLE = True
except ImportError:
    JELLYFISH_AVAILABLE = False

try:
    import phonetics
    PHONETICS_AVAILABLE = True
except ImportError:
    PHONETICS_AVAILABLE = False

# Optional ML and AI libraries
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    np = None

from backend.core.auto_esc_config import get_config_value
from backend.services.openai_service import OpenAIService
from backend.database.database_service import DatabaseService

logger = logging.getLogger(__name__)

@dataclass
class MatchResult:
    """Result of entity matching operation"""
    source_record: Dict[str, Any]
    target_record: Dict[str, Any]
    platform: str
    confidence_score: float
    match_factors: Dict[str, float]
    requires_manual_review: bool
    match_method: str
    processing_time_ms: int
    created_at: datetime

@dataclass
class EntityFeatures:
    """Extracted features for entity matching"""
    name_features: Dict[str, float]
    email_features: Dict[str, float]
    title_features: Dict[str, float]
    platform_features: Dict[str, float]
    temporal_features: Dict[str, float]
    composite_score: float

class AdvancedEntityMatcher:
    """Advanced entity matching with multiple algorithms and confidence scoring"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.db_service = DatabaseService()
        
        # Initialize basic matchers (with fallbacks)
        self.use_advanced_matching = FUZZYWUZZY_AVAILABLE and SKLEARN_AVAILABLE
        logger.info(f"Entity matcher initialized with advanced matching: {self.use_advanced_matching}")
        
        # Algorithm weights for composite scoring
        self.weights = {
            'exact': 0.35,
            'fuzzy': 0.25, 
            'semantic': 0.20,
            'probabilistic': 0.15,
            'ml': 0.05  # Lower weight initially, increases as model improves
        }
        
        # Confidence thresholds
        self.thresholds = {
            'auto_merge': 0.95,
            'high_confidence': 0.85,
            'manual_review': 0.50,
            'reject': 0.30
        }
        
    async def match_employee_across_platforms(
        self, 
        source_employee: Dict[str, Any],
        target_platform: str,
        target_records: List[Dict[str, Any]],
        confidence_threshold: float = 0.5
    ) -> List[MatchResult]:
        """
        Advanced employee matching across platforms with confidence scoring
        """
        start_time = datetime.now()
        match_results = []
        
        logger.info(f"Starting entity matching for {source_employee.get('name', 'Unknown')} against {len(target_records)} records in {target_platform}")
        
        for target_record in target_records:
            try:
                # Check cache first
                cache_key = self._generate_cache_key(source_employee, target_record)
                cached_result = await self.cache_manager.get_similarity_score(cache_key)
                
                if cached_result:
                    logger.debug(f"Using cached similarity score: {cached_result['similarity_score']}")
                    match_results.append(self._create_match_result_from_cache(
                        source_employee, target_record, target_platform, cached_result, start_time
                    ))
                    continue
                
                # Layer 1: Exact matching
                exact_score = await self._exact_match_score(source_employee, target_record)
                
                # Layer 2: Fuzzy string matching
                fuzzy_score = await self._fuzzy_string_match_score(source_employee, target_record)
                
                # Layer 3: Semantic similarity
                semantic_score = await self._semantic_match_score(source_employee, target_record)
                
                # Layer 4: Probabilistic matching
                probabilistic_score = await self._probabilistic_match_score(source_employee, target_record)
                
                # Layer 5: ML-powered matching
                ml_score = await self.ml_matcher.predict_match_probability(source_employee, target_record)
                
                # Weighted composite score
                composite_score = self._calculate_composite_score(
                    exact_score, fuzzy_score, semantic_score, probabilistic_score, ml_score
                )
                
                processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                if composite_score >= confidence_threshold:
                    match_result = MatchResult(
                        source_record=source_employee,
                        target_record=target_record,
                        platform=target_platform,
                        confidence_score=composite_score,
                        match_factors={
                            "exact": exact_score,
                            "fuzzy": fuzzy_score,
                            "semantic": semantic_score,
                            "probabilistic": probabilistic_score,
                            "ml": ml_score
                        },
                        requires_manual_review=composite_score < self.thresholds['high_confidence'],
                        match_method=self._determine_primary_match_method(exact_score, fuzzy_score, semantic_score, probabilistic_score, ml_score),
                        processing_time_ms=processing_time,
                        created_at=datetime.now()
                    )
                    
                    match_results.append(match_result)
                    
                    # Cache the result for future use
                    await self.cache_manager.store_similarity_score(
                        cache_key, composite_score, {
                            "exact": exact_score,
                            "fuzzy": fuzzy_score,
                            "semantic": semantic_score,
                            "probabilistic": probabilistic_score,
                            "ml": ml_score
                        }
                    )
                
            except Exception as e:
                logger.error(f"Error matching entities: {e}", exc_info=True)
                continue
        
        # Sort by confidence score (highest first)
        match_results.sort(key=lambda x: x.confidence_score, reverse=True)
        
        total_time = int((datetime.now() - start_time).total_seconds() * 1000)
        logger.info(f"Entity matching completed in {total_time}ms. Found {len(match_results)} potential matches")
        
        return match_results
    
    async def _exact_match_score(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> float:
        """Calculate exact match score using unique identifiers"""
        score = 0.0
        matches = 0
        total_checks = 0
        
        # Email exact match (highest priority)
        email1 = self._normalize_email(entity1.get('email', ''))
        email2 = self._normalize_email(entity2.get('email', ''))
        if email1 and email2:
            total_checks += 1
            if email1 == email2:
                score += 1.0
                matches += 1
        
        # Phone number exact match
        phone1 = self._normalize_phone(entity1.get('phone', ''))
        phone2 = self._normalize_phone(entity2.get('phone', ''))
        if phone1 and phone2:
            total_checks += 1
            if phone1 == phone2:
                score += 1.0
                matches += 1
        
        # Platform-specific ID matches
        for id_field in ['employee_id', 'user_id', 'contact_id', 'person_id']:
            id1 = entity1.get(id_field, '')
            id2 = entity2.get(id_field, '')
            if id1 and id2:
                total_checks += 1
                if id1 == id2:
                    score += 1.0
                    matches += 1
        
        return score / max(total_checks, 1) if total_checks > 0 else 0.0
    
    async def _fuzzy_string_match_score(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> float:
        """Calculate fuzzy string matching score"""
        name1 = entity1.get('name', '') or f"{entity1.get('first_name', '')} {entity1.get('last_name', '')}".strip()
        name2 = entity2.get('name', '') or f"{entity2.get('first_name', '')} {entity2.get('last_name', '')}".strip()
        
        if not name1 or not name2:
            return 0.0
        
        # Name similarity using multiple algorithms
        name_similarity = self.name_matcher.calculate_name_similarity(name1, name2)
        
        # Email similarity
        email_similarity = self.email_matcher.calculate_email_similarity(
            entity1.get('email', ''), entity2.get('email', '')
        )
        
        # Title similarity
        title_similarity = self.title_matcher.calculate_title_similarity(
            entity1.get('title', ''), entity2.get('title', '')
        )
        
        # Weighted average based on available data
        weights = []
        scores = []
        
        if name_similarity > 0:
            weights.append(0.5)
            scores.append(name_similarity)
        
        if email_similarity > 0:
            weights.append(0.3)
            scores.append(email_similarity)
        
        if title_similarity > 0:
            weights.append(0.2)
            scores.append(title_similarity)
        
        if not scores:
            return 0.0
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        return sum(score * weight for score, weight in zip(scores, normalized_weights))
    
    async def _semantic_match_score(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> float:
        """Calculate semantic similarity using AI embeddings"""
        return await self.semantic_matcher.calculate_semantic_similarity(entity1, entity2)
    
    async def _probabilistic_match_score(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> float:
        """Calculate probabilistic matching score using multiple fields"""
        factors = []
        
        # Name + email domain consistency
        email1_domain = self._extract_email_domain(entity1.get('email', ''))
        email2_domain = self._extract_email_domain(entity2.get('email', ''))
        if email1_domain and email2_domain and email1_domain == email2_domain:
            name_sim = self.name_matcher.calculate_name_similarity(
                entity1.get('name', ''), entity2.get('name', '')
            )
            factors.append(name_sim * 0.8)  # High weight for same domain + similar name
        
        # Title + department consistency
        title1 = entity1.get('title', '').lower()
        title2 = entity2.get('title', '').lower()
        dept1 = entity1.get('department', '').lower()
        dept2 = entity2.get('department', '').lower()
        
        if title1 and title2 and dept1 and dept2:
            title_sim = fuzz.ratio(title1, title2) / 100.0
            dept_sim = fuzz.ratio(dept1, dept2) / 100.0
            factors.append((title_sim + dept_sim) / 2 * 0.6)
        
        # Temporal patterns (joining dates, last activity)
        temporal_sim = self._calculate_temporal_similarity(entity1, entity2)
        if temporal_sim > 0:
            factors.append(temporal_sim * 0.4)
        
        return sum(factors) / len(factors) if factors else 0.0
    
    def _calculate_composite_score(self, exact: float, fuzzy: float, semantic: float, probabilistic: float, ml: float) -> float:
        """Calculate weighted composite score"""
        return (
            exact * self.weights['exact'] +
            fuzzy * self.weights['fuzzy'] +
            semantic * self.weights['semantic'] +
            probabilistic * self.weights['probabilistic'] +
            ml * self.weights['ml']
        )
    
    def _determine_primary_match_method(self, exact: float, fuzzy: float, semantic: float, probabilistic: float, ml: float) -> str:
        """Determine which method contributed most to the match"""
        scores = {
            'exact': exact * self.weights['exact'],
            'fuzzy': fuzzy * self.weights['fuzzy'],
            'semantic': semantic * self.weights['semantic'],
            'probabilistic': probabilistic * self.weights['probabilistic'],
            'ml': ml * self.weights['ml']
        }
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _generate_cache_key(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> str:
        """Generate unique cache key for entity pair"""
        def entity_hash(entity):
            key_fields = [
                entity.get('name', ''),
                entity.get('email', ''),
                entity.get('title', ''),
                entity.get('phone', '')
            ]
            return hashlib.md5('|'.join(key_fields).encode()).hexdigest()
        
        hash1 = entity_hash(entity1)
        hash2 = entity_hash(entity2)
        # Ensure consistent ordering
        return f"{min(hash1, hash2)}:{max(hash1, hash2)}"
    
    def _normalize_email(self, email: str) -> str:
        """Normalize email for exact matching"""
        if not email:
            return ''
        return email.lower().strip()
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for exact matching"""
        if not phone:
            return ''
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        # Handle US numbers
        if len(digits) == 10:
            return f"+1{digits}"
        elif len(digits) == 11 and digits.startswith('1'):
            return f"+{digits}"
        return digits
    
    def _extract_email_domain(self, email: str) -> str:
        """Extract domain from email address"""
        if '@' in email:
            return email.split('@')[1].lower()
        return ''
    
    def _calculate_temporal_similarity(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> float:
        """Calculate similarity based on temporal patterns"""
        # This is a placeholder - would implement based on join dates, activity patterns, etc.
        return 0.0
    
    def _create_match_result_from_cache(self, source: Dict, target: Dict, platform: str, cached: Dict, start_time: datetime) -> MatchResult:
        """Create match result from cached data"""
        return MatchResult(
            source_record=source,
            target_record=target,
            platform=platform,
            confidence_score=cached['similarity_score'],
            match_factors=cached['similarity_factors'],
            requires_manual_review=cached['similarity_score'] < self.thresholds['high_confidence'],
            match_method='cached',
            processing_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
            created_at=datetime.now()
        )

class NameMatcher:
    """Advanced name matching with multiple similarity algorithms"""
    
    def __init__(self):
        self.name_prefixes = ['mr', 'mrs', 'ms', 'dr', 'prof']
        self.name_suffixes = ['jr', 'sr', 'ii', 'iii', 'iv']
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate comprehensive name similarity score"""
        if not name1 or not name2:
            return 0.0
        
        # Normalize names (remove titles, clean formatting)
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # Multiple similarity measures
        levenshtein_sim = 1 - (Levenshtein.distance(norm1, norm2) / max(len(norm1), len(norm2)))
        jaro_winkler_sim = jaro_winkler_similarity(norm1, norm2)
        metaphone_sim = self._metaphone_similarity(norm1, norm2)
        token_sim = self._token_set_ratio(norm1, norm2)
        
        # Weighted average based on name characteristics
        if self._has_middle_initial(name1) or self._has_middle_initial(name2):
            # Weight metaphone higher for names with initials
            return (levenshtein_sim * 0.2 + jaro_winkler_sim * 0.3 + 
                   metaphone_sim * 0.4 + token_sim * 0.1)
        else:
            # Standard weighting
            return (levenshtein_sim * 0.3 + jaro_winkler_sim * 0.4 + 
                   metaphone_sim * 0.2 + token_sim * 0.1)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name by removing titles and cleaning format"""
        if not name:
            return ''
        
        # Convert to lowercase and remove extra spaces
        normalized = re.sub(r'\s+', ' ', name.lower().strip())
        
        # Remove common prefixes and suffixes
        tokens = normalized.split()
        cleaned_tokens = []
        
        for token in tokens:
            # Remove periods and commas
            clean_token = token.replace('.', '').replace(',', '')
            if clean_token not in self.name_prefixes and clean_token not in self.name_suffixes:
                cleaned_tokens.append(clean_token)
        
        return ' '.join(cleaned_tokens)
    
    def _has_middle_initial(self, name: str) -> bool:
        """Check if name contains middle initial"""
        tokens = name.split()
        for token in tokens:
            if len(token) == 1 or (len(token) == 2 and token.endswith('.')):
                return True
        return False
    
    def _metaphone_similarity(self, name1: str, name2: str) -> float:
        """Calculate phonetic similarity using metaphone"""
        try:
            metaphone1 = metaphone(name1)
            metaphone2 = metaphone(name2)
            
            if metaphone1 == metaphone2:
                return 1.0
            
            # Use string similarity on metaphone codes
            return fuzz.ratio(metaphone1, metaphone2) / 100.0
        except:
            return 0.0
    
    def _token_set_ratio(self, name1: str, name2: str) -> float:
        """Calculate token set ratio for word-level matching"""
        return fuzz.token_set_ratio(name1, name2) / 100.0

class JobTitleMatcher:
    """Intelligent job title matching with semantic understanding"""
    
    def __init__(self):
        self.title_synonyms = {
            "ceo": ["chief executive officer", "founder", "president & ceo", "managing partner", "executive director"],
            "cpo": ["chief product officer", "vp product", "head of product", "product director"],
            "cfo": ["chief financial officer", "vp finance", "finance director", "financial director"],
            "cto": ["chief technology officer", "vp engineering", "head of engineering", "technical director"],
            "vp": ["vice president", "senior vice president", "svp", "assistant vice president", "avp"],
            "director": ["dir", "head of", "manager", "senior manager"],
            "engineer": ["developer", "programmer", "software engineer", "software developer"],
            "analyst": ["associate", "specialist", "coordinator"]
        }
        
        self.hierarchy_levels = {
            "c_level": ["ceo", "cfo", "cto", "cpo", "chief"],
            "vp_level": ["vp", "vice president", "svp"],
            "director_level": ["director", "head of"],
            "manager_level": ["manager", "senior manager"],
            "individual_contributor": ["engineer", "analyst", "specialist", "coordinator"]
        }
    
    def calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate job title similarity with semantic understanding"""
        if not title1 or not title2:
            return 0.0
        
        # Normalize titles
        norm1 = self._normalize_title(title1)
        norm2 = self._normalize_title(title2)
        
        # Check exact synonyms first
        if self._are_synonymous_titles(norm1, norm2):
            return 1.0
        
        # Fuzzy string similarity
        string_sim = fuzz.ratio(norm1, norm2) / 100.0
        
        # Hierarchical similarity (same level)
        hierarchy_sim = self._calculate_hierarchy_similarity(norm1, norm2)
        
        # Token overlap similarity
        token_sim = fuzz.token_set_ratio(norm1, norm2) / 100.0
        
        return max(string_sim * 0.4 + hierarchy_sim * 0.3 + token_sim * 0.3, 0.0)
    
    def _normalize_title(self, title: str) -> str:
        """Normalize job title"""
        if not title:
            return ''
        
        # Convert to lowercase and remove extra spaces
        normalized = re.sub(r'\s+', ' ', title.lower().strip())
        
        # Remove common noise words
        noise_words = ['the', 'of', 'and', '&', '-']
        tokens = normalized.split()
        cleaned_tokens = [token for token in tokens if token not in noise_words]
        
        return ' '.join(cleaned_tokens)
    
    def _are_synonymous_titles(self, title1: str, title2: str) -> bool:
        """Check if titles are synonymous"""
        for key, synonyms in self.title_synonyms.items():
            if (title1 in synonyms or title1 == key) and (title2 in synonyms or title2 == key):
                return True
        return False
    
    def _calculate_hierarchy_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity based on hierarchy level"""
        level1 = self._get_hierarchy_level(title1)
        level2 = self._get_hierarchy_level(title2)
        
        if level1 == level2:
            return 1.0
        elif abs(list(self.hierarchy_levels.keys()).index(level1) - 
                list(self.hierarchy_levels.keys()).index(level2)) <= 1:
            return 0.7
        else:
            return 0.3
    
    def _get_hierarchy_level(self, title: str) -> str:
        """Determine hierarchy level of title"""
        for level, keywords in self.hierarchy_levels.items():
            for keyword in keywords:
                if keyword in title:
                    return level
        return "individual_contributor"

class EmailMatcher:
    """Advanced email matching with domain intelligence"""
    
    def calculate_email_similarity(self, email1: str, email2: str) -> float:
        """Calculate email similarity with domain and pattern analysis"""
        if not email1 or not email2:
            return 0.0
        
        email1 = email1.lower().strip()
        email2 = email2.lower().strip()
        
        if email1 == email2:
            return 1.0
        
        # Split into username and domain
        try:
            user1, domain1 = email1.split('@')
            user2, domain2 = email2.split('@')
        except ValueError:
            return 0.0
        
        # Domain matching (same company)
        domain_match = 1.0 if domain1 == domain2 else 0.0
        
        # Username pattern matching
        username_sim = self._calculate_username_similarity(user1, user2)
        
        # Pattern analysis (firstname.lastname vs flastname)
        pattern_sim = self._analyze_email_patterns(user1, user2, domain_match > 0)
        
        return domain_match * 0.4 + username_sim * 0.4 + pattern_sim * 0.2
    
    def _calculate_username_similarity(self, user1: str, user2: str) -> float:
        """Calculate username similarity"""
        if user1 == user2:
            return 1.0
        
        # Direct fuzzy similarity
        fuzzy_sim = fuzz.ratio(user1, user2) / 100.0
        
        # Check for common patterns
        pattern_sim = self._check_username_patterns(user1, user2)
        
        return max(fuzzy_sim, pattern_sim)
    
    def _analyze_email_patterns(self, user1: str, user2: str, same_domain: bool) -> float:
        """Analyze email patterns for similarity"""
        if not same_domain:
            return 0.0
        
        # Common patterns: firstname.lastname, firstlast, flastname
        patterns1 = self._extract_name_patterns(user1)
        patterns2 = self._extract_name_patterns(user2)
        
        # Check if any patterns match
        for p1 in patterns1:
            for p2 in patterns2:
                if fuzz.ratio(p1, p2) > 80:
                    return 0.8
        
        return 0.0
    
    def _check_username_patterns(self, user1: str, user2: str) -> float:
        """Check for common username patterns"""
        # Remove numbers and special characters for pattern matching
        clean1 = re.sub(r'[^a-z]', '', user1)
        clean2 = re.sub(r'[^a-z]', '', user2)
        
        if clean1 == clean2:
            return 0.9
        
        # Check for initials + lastname pattern
        if len(clean1) >= 3 and len(clean2) >= 3:
            if clean1[0] == clean2[0] and clean1[1:] == clean2[1:]:
                return 0.8
        
        return fuzz.ratio(clean1, clean2) / 100.0
    
    def _extract_name_patterns(self, username: str) -> List[str]:
        """Extract possible name patterns from username"""
        patterns = [username]
        
        # Split on common separators
        separators = ['.', '_', '-']
        for sep in separators:
            if sep in username:
                parts = username.split(sep)
                if len(parts) == 2:
                    patterns.extend([
                        parts[0] + parts[1],  # firstlast
                        parts[0][0] + parts[1],  # flastname
                        parts[0] + parts[1][0]  # firstnamel
                    ])
        
        return patterns

class SemanticMatcher:
    """Semantic matching using OpenAI embeddings"""
    
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        self.embedding_cache = {}
    
    async def calculate_semantic_similarity(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> float:
        """Calculate semantic similarity using embeddings"""
        try:
            # Create semantic representations
            text1 = self._create_semantic_text(entity1)
            text2 = self._create_semantic_text(entity2)
            
            if not text1 or not text2:
                return 0.0
            
            # Get embeddings (with caching)
            embedding1 = await self._get_embedding(text1)
            embedding2 = await self._get_embedding(text2)
            
            # Calculate cosine similarity
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            
            # Normalize to 0-1 range (cosine similarity can be -1 to 1)
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return 0.0
    
    def _create_semantic_text(self, entity: Dict[str, Any]) -> str:
        """Create semantic text representation of entity"""
        parts = []
        
        # Name
        name = entity.get('name', '') or f"{entity.get('first_name', '')} {entity.get('last_name', '')}".strip()
        if name:
            parts.append(f"Name: {name}")
        
        # Title
        title = entity.get('title', '')
        if title:
            parts.append(f"Title: {title}")
        
        # Department
        department = entity.get('department', '')
        if department:
            parts.append(f"Department: {department}")
        
        # Company
        company = entity.get('company', '')
        if company:
            parts.append(f"Company: {company}")
        
        return '. '.join(parts)
    
    async def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text with caching"""
        cache_key = hashlib.md5(text.encode()).hexdigest()
        
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        try:
            embedding = await self.openai_service.get_embedding(text)
            self.embedding_cache[cache_key] = np.array(embedding)
            return self.embedding_cache[cache_key]
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return np.zeros(1536)  # Default OpenAI embedding dimension

class MLEntityMatcher:
    """Machine learning-powered entity matching (placeholder for now)"""
    
    def __init__(self):
        self.model_loaded = False
    
    async def predict_match_probability(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> float:
        """Predict match probability using ML model"""
        # For now, return a simple heuristic
        # In production, this would use a trained ML model
        return 0.5
    
    async def learn_from_confirmation(self, entity1: Dict[str, Any], entity2: Dict[str, Any], is_match: bool):
        """Learn from manual confirmations"""
        # Placeholder for ML training
        pass
    
    def basic_entity_match(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> MatchResult:
        """
        Basic entity matching without external dependencies
        Fallback implementation when advanced libraries are not available
        """
        start_time = datetime.now()
        
        # Basic string matching
        name1 = entity1.get('full_name', '').lower().strip()
        name2 = entity2.get('full_name', '').lower().strip()
        email1 = entity1.get('email', '').lower().strip()
        email2 = entity2.get('email', '').lower().strip()
        
        # Exact match checking
        exact_name_match = name1 == name2
        exact_email_match = email1 == email2 and email1 != ''
        
        # Basic similarity scoring
        name_similarity = 1.0 if exact_name_match else 0.0
        email_similarity = 1.0 if exact_email_match else 0.0
        
        # Simple substring matching for partial matches
        if not exact_name_match and name1 and name2:
            # Check if names contain each other
            if name1 in name2 or name2 in name1:
                name_similarity = 0.7
            else:
                # Check for common words
                words1 = set(name1.split())
                words2 = set(name2.split())
                common_words = words1 & words2
                if common_words:
                    name_similarity = len(common_words) / max(len(words1), len(words2))
        
        # Email domain matching
        if not exact_email_match and email1 and email2:
            domain1 = email1.split('@')[-1] if '@' in email1 else ''
            domain2 = email2.split('@')[-1] if '@' in email2 else ''
            if domain1 == domain2 and domain1:
                email_similarity = 0.5
        
        # Overall confidence calculation
        factors = {
            'name_similarity': name_similarity,
            'email_similarity': email_similarity,
            'exact_match': exact_name_match or exact_email_match
        }
        
        # Weighted confidence score
        confidence = (name_similarity * 0.6 + email_similarity * 0.4)
        
        # Determine if manual review needed
        requires_review = 0.3 < confidence < 0.9
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return MatchResult(
            source_record=entity1,
            target_record=entity2,
            platform='basic_matcher',
            confidence_score=confidence,
            match_factors=factors,
            requires_manual_review=requires_review,
            match_method='basic_string_matching',
            processing_time_ms=processing_time,
            created_at=datetime.now()
        )

class SimilarityCacheManager:
    """Manage similarity score caching for performance"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.cache_ttl_hours = 24
        self.algorithm_version = "1.0"
    
    async def get_similarity_score(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached similarity score if available and not expired"""
        try:
            query = """
            SELECT similarity_score, similarity_factors, algorithm_version, expires_at
            FROM FOUNDATIONAL_KNOWLEDGE.ENTITY_SIMILARITY_CACHE
            WHERE cache_id = %s AND expires_at > CURRENT_TIMESTAMP
            """
            result = await self.db_service.execute_query(query, [cache_key])
            
            if result and len(result) > 0:
                row = result[0]
                return {
                    'similarity_score': float(row['similarity_score']),
                    'similarity_factors': row['similarity_factors'],
                    'algorithm_version': row['algorithm_version']
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached similarity score: {e}")
            return None
    
    async def store_similarity_score(self, cache_key: str, score: float, factors: Dict[str, float]) -> bool:
        """Store similarity score in cache"""
        try:
            expires_at = datetime.now() + timedelta(hours=self.cache_ttl_hours)
            
            query = """
            INSERT INTO FOUNDATIONAL_KNOWLEDGE.ENTITY_SIMILARITY_CACHE 
            (cache_id, entity1_hash, entity2_hash, similarity_score, similarity_factors, 
             algorithm_version, expires_at, computation_time_ms)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (cache_id) DO UPDATE SET
                similarity_score = EXCLUDED.similarity_score,
                similarity_factors = EXCLUDED.similarity_factors,
                algorithm_version = EXCLUDED.algorithm_version,
                expires_at = EXCLUDED.expires_at
            """
            
            # Split cache_key to get entity hashes
            entity_hashes = cache_key.split(':')
            entity1_hash = entity_hashes[0] if len(entity_hashes) > 0 else cache_key[:32]
            entity2_hash = entity_hashes[1] if len(entity_hashes) > 1 else cache_key[32:]
            
            await self.db_service.execute_query(query, [
                cache_key, entity1_hash, entity2_hash, score, 
                json.dumps(factors), self.algorithm_version, expires_at, 0
            ])
            
            return True
        except Exception as e:
            logger.error(f"Error storing similarity score in cache: {e}")
            return False
    
    async def clear_expired_cache(self):
        """Clear expired cache entries"""
        try:
            query = """
            DELETE FROM FOUNDATIONAL_KNOWLEDGE.ENTITY_SIMILARITY_CACHE
            WHERE expires_at < CURRENT_TIMESTAMP
            """
            await self.db_service.execute_query(query)
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
