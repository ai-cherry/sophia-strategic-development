#!/usr/bin/env python3
from __future__ import annotations

"""
Graphiti Enhanced Memory for Sophia AI
Enhances existing AI Memory MCP server with temporal knowledge graphs
"""

import asyncio
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass
class MemoryNode:
    """Node in the temporal knowledge graph"""

    node_id: str
    node_type: str
    name: str
    properties: dict[str, Any]
    created_at: datetime


@dataclass
class MemoryRelationship:
    """Relationship between nodes"""

    relationship_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    strength: float
    created_at: datetime


class GraphitiEnhancedMemory:
    """
    Graphiti-enhanced memory system that adds temporal knowledge graphs
    to our existing AI Memory capabilities.
    """

    def __init__(self):
        self.nodes: dict[str, MemoryNode] = {}
        self.relationships: dict[str, MemoryRelationship] = {}

        # Business entity types for Sophia AI
        self.business_node_types = {
            "PERSON": ["employee", "customer", "prospect", "executive"],
            "COMPANY": ["client", "competitor", "vendor", "partner"],
            "DEAL": ["opportunity", "proposal", "contract"],
            "PROJECT": ["initiative", "campaign", "implementation"],
            "DECISION": ["strategic", "tactical", "operational"],
            "INSIGHT": ["market", "competitive", "performance"],
        }

    async def initialize(self) -> None:
        """Initialize Graphiti enhanced memory"""
        logger.info("Graphiti Enhanced Memory initialized (in-memory mode)")

    async def cleanup(self) -> None:
        """Cleanup resources"""
        self.nodes.clear()
        self.relationships.clear()

    async def store_business_entity(
        self, entity_type: str, name: str, properties: dict[str, Any]
    ) -> str:
        """Store a business entity in the knowledge graph"""
        try:
            node_id = str(uuid.uuid4())
            node = MemoryNode(
                node_id=node_id,
                node_type=entity_type,
                name=name,
                properties=properties,
                created_at=datetime.now(UTC),
            )

            self.nodes[node_id] = node
            logger.info(f"Stored {entity_type} entity: {name} (ID: {node_id})")
            return node_id

        except Exception as e:
            logger.error(f"Error storing business entity: {e}")
            return str(uuid.uuid4())

    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: dict[str, Any] | None = None,
        strength: float = 1.0,
    ) -> str:
        """Create a relationship between entities"""
        try:
            relationship_id = str(uuid.uuid4())
            relationship = MemoryRelationship(
                relationship_id=relationship_id,
                source_node_id=source_id,
                target_node_id=target_id,
                relationship_type=relationship_type,
                strength=strength,
                created_at=datetime.now(UTC),
            )

            self.relationships[relationship_id] = relationship
            logger.info(
                f"Created relationship: {relationship_type} (ID: {relationship_id})"
            )
            return relationship_id

        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return str(uuid.uuid4())

    async def find_related_entities(
        self, entity_id: str, max_depth: int = 2
    ) -> list[dict[str, Any]]:
        """Find entities related to a given entity"""
        try:
            related_entities = []
            visited = set()

            def find_connections(current_id: str, depth: int):
                if depth > max_depth or current_id in visited:
                    return

                visited.add(current_id)

                for rel in self.relationships.values():
                    if (
                        rel.source_node_id == current_id
                        and rel.target_node_id in self.nodes
                    ):
                        target_node = self.nodes[rel.target_node_id]
                        related_entities.append(
                            {
                                "node_id": target_node.node_id,
                                "name": target_node.name,
                                "type": target_node.node_type,
                                "relationship_type": rel.relationship_type,
                                "strength": rel.strength,
                                "depth": depth,
                            }
                        )
                        find_connections(rel.target_node_id, depth + 1)

                    elif (
                        rel.target_node_id == current_id
                        and rel.source_node_id in self.nodes
                    ):
                        source_node = self.nodes[rel.source_node_id]
                        related_entities.append(
                            {
                                "node_id": source_node.node_id,
                                "name": source_node.name,
                                "type": source_node.node_type,
                                "relationship_type": rel.relationship_type,
                                "strength": rel.strength,
                                "depth": depth,
                            }
                        )
                        find_connections(rel.source_node_id, depth + 1)

            find_connections(entity_id, 1)
            return related_entities

        except Exception as e:
            logger.error(f"Error finding related entities: {e}")
            return []

    async def enhance_memory_with_graph(
        self, memory_content: str, memory_category: str, entities: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Enhance stored memory with knowledge graph relationships"""
        try:
            entity_ids = []
            for entity in entities:
                entity_id = await self.store_business_entity(
                    entity_type=entity.get("type", "INSIGHT"),
                    name=entity.get("name", "Unknown"),
                    properties=entity.get("properties", {}),
                )
                entity_ids.append(entity_id)

            relationships_created = 0
            for i, source_id in enumerate(entity_ids):
                for target_id in entity_ids[i + 1 :]:
                    await self.create_relationship(
                        source_id=source_id,
                        target_id=target_id,
                        relationship_type="RELATES_TO",
                        strength=0.7,
                    )
                    relationships_created += 1

            return {
                "success": True,
                "entities_stored": len(entity_ids),
                "relationships_created": relationships_created,
                "entity_ids": entity_ids,
            }

        except Exception as e:
            logger.error(f"Error enhancing memory with graph: {e}")
            return {"success": False, "error": str(e)}

    def get_stats(self) -> dict[str, Any]:
        """Get knowledge graph statistics"""
        return {
            "total_nodes": len(self.nodes),
            "total_relationships": len(self.relationships),
            "node_types": list({node.node_type for node in self.nodes.values()}),
            "relationship_types": list(
                {rel.relationship_type for rel in self.relationships.values()}
            ),
        }


# Integration functions
async def create_graphiti_enhancement() -> GraphitiEnhancedMemory:
    """Create and initialize Graphiti enhancement"""
    graphiti = GraphitiEnhancedMemory()
    await graphiti.initialize()
    return graphiti


if __name__ == "__main__":

    async def test():
        graphiti = await create_graphiti_enhancement()

        # Test storing entities
        deal_id = await graphiti.store_business_entity(
            "DEAL", "Acme Corp Deal", {"value": 100000}
        )
        person_id = await graphiti.store_business_entity(
            "PERSON", "John Smith", {"role": "CEO"}
        )

        # Test relationship
        await graphiti.create_relationship(person_id, deal_id, "OWNS")

        # Test finding related entities
        related = await graphiti.find_related_entities(deal_id)
        print(f"Related entities: {related}")

        # Get stats
        stats = graphiti.get_stats()
        print(f"Graph stats: {stats}")

        await graphiti.cleanup()

    asyncio.run(test())
