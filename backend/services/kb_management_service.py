#!/usr/bin/env python3
"""
Knowledge Base Management Service
Natural language-driven KB entity and article management with NLU capabilities
"""

import asyncio
import json
import logging
import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

# Core imports
from backend.core.auto_esc_config import get_config_value
from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.services.foundational_knowledge_service import FoundationalKnowledgeService
from backend.mcp.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer

logger = logging.getLogger(__name__)


class KBEntityType(Enum):
    """Supported KB entity types"""
    EMPLOYEE = "employee"
    CUSTOMER = "customer"
    PRODUCT = "product"
    COMPETITOR = "competitor"
    PROCESS = "process"
    VALUE = "value"
    ARTICLE = "article"


class KBOperation(Enum):
    """KB management operations"""
    ADD = "add"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    UPLOAD = "upload"


@dataclass
class KBEntity:
    """Knowledge Base entity structure"""
    entity_type: KBEntityType
    entity_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_by: str = "kb_management_service"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_type": self.entity_type.value,
            "entity_id": self.entity_id,
            "attributes": self.attributes,
            "metadata": self.metadata,
            "created_by": self.created_by
        }


@dataclass
class KBProcessingResult:
    """Result of KB processing operation"""
    success: bool
    operation: KBOperation
    entity_type: Optional[KBEntityType] = None
    entity_id: Optional[str] = None
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class NaturalLanguageKBProcessor:
    """Natural language processor for KB operations"""
    
    def __init__(self):
        self.entity_patterns = self._initialize_entity_patterns()
        self.operation_patterns = self._initialize_operation_patterns()
        self.attribute_extractors = self._initialize_attribute_extractors()
        self.openai_client = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize NLP processor"""
        if self.initialized:
            return
        
        try:
            import openai
            api_key = await get_config_value("openai_api_key")
            if api_key:
                self.openai_client = openai.AsyncOpenAI(api_key=api_key)
                logger.info("✅ NL KB Processor initialized with OpenAI")
            else:
                logger.warning("OpenAI API key not available")
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize NL KB Processor: {e}")
            self.initialized = True
    
    def _initialize_entity_patterns(self) -> Dict[KBEntityType, Dict[str, Any]]:
        """Initialize entity type detection patterns"""
        return {
            KBEntityType.EMPLOYEE: {
                "keywords": ["employee", "person", "staff", "team member"],
                "required_fields": ["name", "full_name"],
                "optional_fields": ["email", "department", "skills", "role"]
            },
            KBEntityType.CUSTOMER: {
                "keywords": ["customer", "client", "company", "account"],
                "required_fields": ["company_name", "name"],
                "optional_fields": ["industry", "tier", "contact"]
            },
            KBEntityType.PRODUCT: {
                "keywords": ["product", "service", "solution", "platform"],
                "required_fields": ["product_name", "name"],
                "optional_fields": ["description", "category", "features"]
            }
        }
    
    def _initialize_operation_patterns(self) -> Dict[KBOperation, List[str]]:
        """Initialize operation detection patterns"""
        return {
            KBOperation.ADD: ["add", "create", "new", "define"],
            KBOperation.SEARCH: ["search", "find", "lookup", "get"]
        }
    
    def _initialize_attribute_extractors(self) -> Dict[str, str]:
        """Initialize attribute extraction patterns"""
        return {
            "name": r"name[:\s]+['\"]?([^'\"]+)['\"]?",
            "email": r"email[:\s]+['\"]?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})['\"]?",
            "department": r"department[:\s]+['\"]?([^'\"]+)['\"]?",
            "skills": r"skills[:\s]+\[([^\]]+)\]",
            "company_name": r"company[_\s]*name[:\s]+['\"]?([^'\"]+)['\"]?",
            "product_name": r"product[_\s]*name[:\s]+['\"]?([^'\"]+)['\"]?"
        }
    
    async def parse_natural_language_command(self, command: str) -> Tuple[KBOperation, KBEntityType, Dict[str, Any]]:
        """Parse natural language command"""
        command_lower = command.lower().strip()
        
        # Detect operation
        operation = self._detect_operation(command_lower)
        
        # Detect entity type
        entity_type = self._detect_entity_type(command_lower)
        
        # Extract attributes
        attributes = self._extract_attributes(command)
        
        return operation, entity_type, attributes
    
    def _detect_operation(self, command: str) -> KBOperation:
        """Detect operation from command"""
        for operation, keywords in self.operation_patterns.items():
            if any(keyword in command for keyword in keywords):
                return operation
        return KBOperation.ADD
    
    def _detect_entity_type(self, command: str) -> KBEntityType:
        """Detect entity type from command"""
        for entity_type, config in self.entity_patterns.items():
            if any(keyword in command for keyword in config["keywords"]):
                return entity_type
        return KBEntityType.EMPLOYEE
    
    def _extract_attributes(self, command: str) -> Dict[str, Any]:
        """Extract attributes from command"""
        attributes = {}
        
        for attr_name, pattern in self.attribute_extractors.items():
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if attr_name == "skills" and value:
                    skills = [skill.strip().strip("'\"") for skill in value.split(",")]
                    attributes[attr_name] = skills
                else:
                    attributes[attr_name] = value
        
        return attributes


class KBManagementService:
    """Knowledge Base Management Service"""
    
    def __init__(self):
        self.nl_processor = NaturalLanguageKBProcessor()
        self.cortex_service = None
        self.foundational_service = None
        self.ai_memory = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize KB management service"""
        if self.initialized:
            return
        
        try:
            await self.nl_processor.initialize()
            
            self.cortex_service = SnowflakeCortexService()
            self.foundational_service = FoundationalKnowledgeService()
            self.ai_memory = EnhancedAiMemoryMCPServer()
            
            await self.ai_memory.initialize()
            
            self.initialized = True
            logger.info("✅ KB Management Service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize KB Management Service: {e}")
            raise
    
    async def process_natural_language_command(self, command: str, user_id: str = "system") -> KBProcessingResult:
        """Process natural language KB management command"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Parse command
            operation, entity_type, attributes = await self.nl_processor.parse_natural_language_command(command)
            
            # Execute operation
            if operation == KBOperation.ADD:
                return await self._add_entity(entity_type, attributes, user_id)
            elif operation == KBOperation.SEARCH:
                return await self._search_knowledge(entity_type, attributes, user_id)
            else:
                return KBProcessingResult(
                    success=False,
                    operation=operation,
                    entity_type=entity_type,
                    message=f"Operation {operation.value} not implemented"
                )
        
        except Exception as e:
            logger.error(f"Error processing KB command: {e}")
            return KBProcessingResult(
                success=False,
                operation=KBOperation.ADD,
                message=f"Processing failed: {str(e)}"
            )
    
    async def _add_entity(self, entity_type: KBEntityType, attributes: Dict[str, Any], user_id: str) -> KBProcessingResult:
        """Add new KB entity"""
        try:
            entity_id = str(uuid.uuid4())
            
            entity = KBEntity(
                entity_type=entity_type,
                entity_id=entity_id,
                attributes=attributes,
                metadata={
                    "created_at": datetime.now().isoformat(),
                    "created_by": user_id,
                    "source": "natural_language_command"
                },
                created_by=user_id
            )
            
            # Store in Snowflake
            success = await self._store_entity_in_snowflake(entity)
            
            if success:
                # Store in AI Memory
                await self._store_entity_in_ai_memory(entity)
                
                return KBProcessingResult(
                    success=True,
                    operation=KBOperation.ADD,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    message=f"Successfully added {entity_type.value}",
                    data=entity.to_dict()
                )
            else:
                return KBProcessingResult(
                    success=False,
                    operation=KBOperation.ADD,
                    entity_type=entity_type,
                    message="Failed to store in database"
                )
        
        except Exception as e:
            logger.error(f"Error adding entity: {e}")
            return KBProcessingResult(
                success=False,
                operation=KBOperation.ADD,
                entity_type=entity_type,
                message=f"Failed to add: {str(e)}"
            )
    
    async def _search_knowledge(self, entity_type: KBEntityType, attributes: Dict[str, Any], user_id: str) -> KBProcessingResult:
        """Search knowledge base"""
        try:
            search_query = attributes.get("query", attributes.get("name", ""))
            
            if entity_type == KBEntityType.EMPLOYEE:
                results = await self.foundational_service.search_employees(search_query, limit=10)
            elif entity_type == KBEntityType.CUSTOMER:
                results = await self.foundational_service.search_customers(search_query, limit=10)
            else:
                results = await self.foundational_service.search_knowledge_base(search_query, limit=10)
            
            return KBProcessingResult(
                success=True,
                operation=KBOperation.SEARCH,
                entity_type=entity_type,
                message=f"Found {len(results)} results",
                data={"results": results, "query": search_query}
            )
        
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return KBProcessingResult(
                success=False,
                operation=KBOperation.SEARCH,
                entity_type=entity_type,
                message=f"Search failed: {str(e)}"
            )
    
    async def _store_entity_in_snowflake(self, entity: KBEntity) -> bool:
        """Store entity in Snowflake"""
        try:
            if entity.entity_type == KBEntityType.EMPLOYEE:
                return await self.foundational_service.create_employee(entity.attributes)
            elif entity.entity_type == KBEntityType.CUSTOMER:
                return await self.foundational_service.create_customer(entity.attributes)
            elif entity.entity_type == KBEntityType.PRODUCT:
                return await self.foundational_service.create_product(entity.attributes)
            return False
        
        except Exception as e:
            logger.error(f"Error storing entity: {e}")
            return False
    
    async def _store_entity_in_ai_memory(self, entity: KBEntity) -> None:
        """Store entity in AI Memory"""
        try:
            content = f"""
            KB Entity: {entity.entity_type.value.title()}
            ID: {entity.entity_id}
            
            Attributes:
            {json.dumps(entity.attributes, indent=2)}
            """
            
            category_mapping = {
                KBEntityType.EMPLOYEE: "foundational_employee",
                KBEntityType.CUSTOMER: "foundational_customer",
                KBEntityType.PRODUCT: "foundational_product"
            }
            
            category = category_mapping.get(entity.entity_type, "foundational_knowledge")
            
            await self.ai_memory.store_memory(
                content=content,
                category=category,
                tags=[entity.entity_type.value, "kb_management"],
                metadata=entity.metadata,
                importance_score=0.7
            )
            
        except Exception as e:
            logger.error(f"Error storing in AI Memory: {e}")
