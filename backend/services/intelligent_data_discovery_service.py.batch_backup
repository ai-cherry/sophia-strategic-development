"""
Intelligent Data Discovery Service
Provides AI-powered analysis and discovery for staged data files
"""

import json
import uuid
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import numpy as np
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    # Fallback for basic data parsing
    pd = None
    np = None


try:
    from backend.services.snowflake_cortex_service import SnowflakeCortexService
except ImportError:
    SnowflakeCortexService = None

try:
    from backend.services.smart_ai_service import SmartAIService
except ImportError:
    SmartAIService = None

try:
    from backend.utils.snowflake_connection import get_snowflake_connection
except ImportError:
    get_snowflake_connection = None


class ChunkingStrategy(Enum):
    """Available chunking strategies for different data types"""

    CONTENT_AWARE = "content-aware"
    ROW_BASED = "row-based"
    SEMANTIC = "semantic"
    RELATIONSHIP_PRESERVING = "relationship-preserving"
    DOCUMENT_SECTION = "document-section"
    TIME_SERIES = "time-series"


class DataQuality(Enum):
    """Data quality assessment levels"""

    EXCELLENT = "excellent"  # 0.9-1.0
    GOOD = "good"  # 0.7-0.89
    FAIR = "fair"  # 0.5-0.69
    POOR = "poor"  # 0.3-0.49
    CRITICAL = "critical"  # 0.0-0.29


@dataclass
class FieldStatistics:
    """Statistics for a single field/column"""

    field_name: str
    data_type: str
    null_count: int
    null_percentage: float
    unique_count: int
    sample_values: list[Any]
    min_value: Any | None = None
    max_value: Any | None = None
    mean_value: float | None = None
    pattern_analysis: dict | None = None
    suggested_type: str | None = None
    quality_score: float = 0.0


@dataclass
class SchemaMapping:
    """Mapping suggestion from source to target schema"""

    source_field: str
    target_field: str
    target_schema: str
    confidence: float
    reasoning: str
    transformation_required: bool = False
    transformation_rules: dict | None = None


@dataclass
class ChunkAnalysis:
    """Analysis results for a chunk of data"""

    chunk_id: str
    chunk_type: str
    content_summary: str
    business_context: str
    quality_score: float
    semantic_coherence: float
    business_relevance: float
    relationships: list[str]


@dataclass
class DataDiscoveryResult:
    """Complete analysis result for a staged file"""

    stage_id: str
    filename: str
    file_type: str
    detected_schema: dict[str, Any]
    field_statistics: list[FieldStatistics]
    suggested_mappings: list[SchemaMapping]
    recommended_target_schema: str
    recommended_chunk_strategy: ChunkingStrategy
    data_quality_score: float
    confidence_score: float
    analysis_summary: str
    content_analysis: dict[str, Any]
    chunk_preview: list[ChunkAnalysis]
    validation_errors: list[str]
    processing_recommendations: dict[str, Any]


class IntelligentDataDiscoveryService:
    """
    AI-powered data discovery and analysis service for staging area
    """

    def __init__(self):
        self.cortex_service = (
            SnowflakeCortexService() if SnowflakeCortexService else None
        )
        self.ai_service = SmartAIService() if SmartAIService else None
        self.target_schemas = {
            "SALESFORCE": [
                "account",
                "contact",
                "opportunity",
                "lead",
                "task",
                "event",
            ],
            "HUBSPOT_DATA": ["deals", "companies", "contacts", "tickets"],
            "GONG_DATA": ["calls", "transcripts", "users", "meetings"],
            "AI_MEMORY": ["memory_records", "categories", "sources"],
            "FOUNDATIONAL_KB": ["documents", "entities", "relationships"],
        }

    async def analyze_staged_file(
        self,
        stage_id: str,
        file_path: str,
        user_id: str,
        analysis_preferences: dict | None = None,
    ) -> DataDiscoveryResult:
        """
        Perform comprehensive AI-powered analysis of a staged file
        """
        try:
            # Load and parse the file
            file_data, file_info = await self._load_file_data(file_path)

            # Perform schema discovery
            detected_schema = await self._discover_schema(file_data, file_info)

            # Calculate field statistics
            field_stats = await self._calculate_field_statistics(
                file_data, detected_schema
            )

            # Analyze content and determine business context
            content_analysis = await self._analyze_content_context(
                file_data, field_stats
            )

            # Suggest target schema mappings
            suggested_mappings = await self._suggest_schema_mappings(
                field_stats, content_analysis, analysis_preferences
            )

            # Recommend target schema
            target_schema = await self._recommend_target_schema(
                suggested_mappings, content_analysis
            )

            # Determine chunking strategy
            chunk_strategy = await self._recommend_chunking_strategy(
                file_info, content_analysis, len(file_data)
            )

            # Generate chunk preview
            chunk_preview = await self._generate_chunk_preview(
                file_data, chunk_strategy, content_analysis
            )

            # Calculate quality scores
            data_quality = self._calculate_data_quality_score(field_stats)
            confidence_score = self._calculate_confidence_score(
                suggested_mappings, content_analysis, data_quality
            )

            # Generate analysis summary
            analysis_summary = await self._generate_analysis_summary(
                detected_schema, suggested_mappings, target_schema, data_quality
            )

            # Validate and identify issues
            validation_errors = await self._validate_data_quality(
                file_data, field_stats
            )

            # Generate processing recommendations
            processing_recommendations = (
                await self._generate_processing_recommendations(
                    file_info, data_quality, chunk_strategy, validation_errors
                )
            )

            # Create discovery result
            result = DataDiscoveryResult(
                stage_id=stage_id,
                filename=file_info["filename"],
                file_type=file_info["file_type"],
                detected_schema=detected_schema,
                field_statistics=field_stats,
                suggested_mappings=suggested_mappings,
                recommended_target_schema=target_schema,
                recommended_chunk_strategy=chunk_strategy,
                data_quality_score=data_quality,
                confidence_score=confidence_score,
                analysis_summary=analysis_summary,
                content_analysis=content_analysis,
                chunk_preview=chunk_preview,
                validation_errors=validation_errors,
                processing_recommendations=processing_recommendations,
            )

            # Store results in staging area
            await self._store_discovery_results(result)

            return result

        except Exception as e:
            raise Exception(f"Data discovery analysis failed: {str(e)}")

    async def _load_file_data(self, file_path: str | Path) -> tuple[list[dict], dict]:
        """Load and parse file data based on type"""
        path_obj = Path(file_path)
        file_info = {
            "filename": path_obj.name,
            "file_type": path_obj.suffix.lower(),
            "size_bytes": path_obj.stat().st_size if path_obj.exists() else 0,
        }

        try:
            if (
                file_info["file_type"] in [".csv", ".tsv"]
                and PANDAS_AVAILABLE
                and pd is not None
            ):
                separator = "\t" if file_info["file_type"] == ".tsv" else ","
                df = pd.read_csv(
                    path_obj, sep=separator, nrows=10000
                )  # Sample first 10k rows
                data = df.to_dict("records")

            elif (
                file_info["file_type"] in [".xlsx", ".xls"]
                and PANDAS_AVAILABLE
                and pd is not None
            ):
                df = pd.read_excel(path_obj, nrows=10000)
                data = df.to_dict("records")

            elif file_info["file_type"] == ".json":
                with open(path_obj) as f:
                    raw_data = json.load(f)
                if isinstance(raw_data, list):
                    data = raw_data[:10000]  # Sample first 10k records
                else:
                    data = [raw_data]

            elif file_info["file_type"] == ".jsonl":
                data = []
                with open(path_obj) as f:
                    for i, line in enumerate(f):
                        if i >= 10000:  # Sample first 10k records
                            break
                        data.append(json.loads(line.strip()))

            elif file_info["file_type"] in [".csv", ".tsv"] and not PANDAS_AVAILABLE:
                # Fallback CSV parsing without pandas
                import csv

                data = []
                separator = "\t" if file_info["file_type"] == ".tsv" else ","
                with open(path_obj, encoding="utf-8") as f:
                    reader = csv.DictReader(f, delimiter=separator)
                    for i, row in enumerate(reader):
                        if i >= 10000:  # Sample first 10k records
                            break
                        data.append(dict(row))

            else:
                # For text files, treat as documents
                with open(path_obj, encoding="utf-8") as f:
                    content = f.read()
                data = [
                    {"document_content": content, "filename": file_info["filename"]}
                ]

            return data, file_info

        except Exception as e:
            raise Exception(f"Failed to load file {path_obj}: {str(e)}")

    async def _discover_schema(
        self, data: list[dict], file_info: dict
    ) -> dict[str, Any]:
        """Discover and analyze the schema structure"""
        if not data:
            return {"fields": [], "record_count": 0}

        schema = {"fields": [], "record_count": len(data)}

        # Analyze field structure from sample data
        all_fields = set()
        for record in data[:1000]:  # Analyze first 1000 records
            all_fields.update(record.keys())

        for field_name in all_fields:
            field_info = {
                "name": field_name,
                "type": "unknown",
                "nullable": False,
                "sample_values": [],
            }

            # Collect sample values and infer type
            values = []
            null_count = 0

            for record in data[:100]:  # Sample from first 100 records
                value = record.get(field_name)
                if value is None or value == "":
                    null_count += 1
                else:
                    values.append(value)
                    if len(field_info["sample_values"]) < 5:
                        field_info["sample_values"].append(str(value))

            # Infer data type
            field_info["type"] = self._infer_data_type(values)
            field_info["nullable"] = null_count > 0

            schema["fields"].append(field_info)

        return schema

    async def _calculate_field_statistics(
        self, data: list[dict], schema: dict[str, Any]
    ) -> list[FieldStatistics]:
        """Calculate comprehensive statistics for each field"""
        stats = []

        for field_info in schema["fields"]:
            field_name = field_info["name"]

            # Collect all values for this field
            values = []
            null_count = 0

            for record in data:
                value = record.get(field_name)
                if value is None or value == "":
                    null_count += 1
                else:
                    values.append(value)

            total_count = len(data)
            null_percentage = (null_count / total_count) * 100 if total_count > 0 else 0
            unique_values = list({str(v) for v in values})
            unique_count = len(unique_values)

            # Calculate basic statistics
            min_val = max_val = mean_val = None
            if values and field_info["type"] in ["integer", "float"]:
                try:
                    numeric_values = [float(v) for v in values if v is not None]
                    if numeric_values:
                        min_val = min(numeric_values)
                        max_val = max(numeric_values)
                        mean_val = sum(numeric_values) / len(numeric_values)
                except Exception:
                    pass

            # Pattern analysis
            pattern_analysis = await self._analyze_field_patterns(
                values, field_info["type"]
            )

            # Suggest improved type
            suggested_type = await self._suggest_field_type(values, pattern_analysis)

            # Calculate quality score
            quality_score = self._calculate_field_quality_score(
                null_percentage, unique_count, total_count, pattern_analysis
            )

            field_stat = FieldStatistics(
                field_name=field_name,
                data_type=field_info["type"],
                null_count=null_count,
                null_percentage=null_percentage,
                unique_count=unique_count,
                sample_values=unique_values[:10],
                min_value=min_val,
                max_value=max_val,
                mean_value=mean_val,
                pattern_analysis=pattern_analysis,
                suggested_type=suggested_type,
                quality_score=quality_score,
            )

            stats.append(field_stat)

        return stats

    async def _analyze_content_context(
        self, data: list[dict], field_stats: list[FieldStatistics]
    ) -> dict[str, Any]:
        """Analyze content to understand business context and domain"""
        try:
            # Prepare sample data for AI analysis
            sample_records = data[:5] if len(data) > 5 else data
            field_names = [stat.field_name for stat in field_stats]

            if self.ai_service is None:
                return self._fallback_content_analysis(field_names, sample_records)

            # Create analysis prompt
            analysis_prompt = f"""
            Analyze this data sample to determine business context and domain:

            Field Names: {', '.join(field_names)}

            Sample Records:
            {json.dumps(sample_records, indent=2)[:2000]}

            Please analyze and provide:
            1. Business domain (e.g., CRM, Sales, Marketing, Financial, HR, etc.)
            2. Data type classification (e.g., customer data, transaction data, communication data)
            3. Key business entities identified
            4. Relationships between fields
            5. Suggested use cases for this data
            6. Data sensitivity level (public, internal, confidential, restricted)

            Respond in JSON format with these exact keys:
            {{
                "business_domain": "string",
                "data_classification": "string",
                "key_entities": ["entity1", "entity2"],
                "field_relationships": {{"field1": "relates_to_field2"}},
                "suggested_use_cases": ["use_case_1", "use_case_2"],
                "sensitivity_level": "string",
                "confidence": 0.85
            }}
            """

            # Get AI analysis - using a basic completion method
            try:
                ai_response = None
                if self.ai_service and hasattr(self.ai_service, "generate_completion"):
                    ai_response = await self.ai_service.generate_completion(
                        messages=[{"role": "user", "content": analysis_prompt}],
                        task_type="data_analysis",
                        context="business_intelligence",
                    )
                elif self.ai_service and hasattr(self.ai_service, "complete"):
                    ai_response = await self.ai_service.complete(analysis_prompt)
                elif self.ai_service and hasattr(self.ai_service, "chat_completion"):
                    ai_response = await self.ai_service.chat_completion(analysis_prompt)
                else:
                    # Fallback if no suitable method found
                    return self._fallback_content_analysis(field_names, sample_records)

                if ai_response:
                    content_analysis = json.loads(ai_response)
                else:
                    content_analysis = self._fallback_content_analysis(
                        field_names, sample_records
                    )
            except Exception:
                # Fallback analysis if AI response is not valid JSON or any error occurs
                content_analysis = self._fallback_content_analysis(
                    field_names, sample_records
                )

            # Add additional analysis
            content_analysis["total_records"] = len(data)
            content_analysis["total_fields"] = len(field_stats)
            content_analysis["data_completeness"] = self._calculate_data_completeness(
                field_stats
            )

            return content_analysis

        except Exception:
            # Return fallback analysis
            return self._fallback_content_analysis(
                [stat.field_name for stat in field_stats], data[:5]
            )

    async def _suggest_schema_mappings(
        self,
        field_stats: list[FieldStatistics],
        content_analysis: dict[str, Any],
        preferences: dict | None = None,
    ) -> list[SchemaMapping]:
        """Generate AI-powered schema mapping suggestions"""
        mappings = []
        business_domain = content_analysis.get("business_domain", "unknown")

        # Determine most likely target schemas based on content analysis
        target_candidates = self._get_target_schema_candidates(
            business_domain, content_analysis
        )

        for field_stat in field_stats:
            field_stat.field_name.lower()

            # Generate mapping suggestions for each candidate schema
            for schema_name in target_candidates:
                target_fields = self.target_schemas.get(schema_name, [])

                # Find best matching target field
                best_match = await self._find_best_field_match(
                    field_stat, target_fields, schema_name
                )

                if best_match:
                    mapping = SchemaMapping(
                        source_field=field_stat.field_name,
                        target_field=best_match["field"],
                        target_schema=schema_name,
                        confidence=best_match["confidence"],
                        reasoning=best_match["reasoning"],
                        transformation_required=best_match.get(
                            "transformation_required", False
                        ),
                        transformation_rules=best_match.get("transformation_rules"),
                    )
                    mappings.append(mapping)

        # Sort by confidence and return top suggestions
        mappings.sort(key=lambda x: x.confidence, reverse=True)
        return mappings[:20]  # Return top 20 mappings

    async def _recommend_target_schema(
        self, mappings: list[SchemaMapping], content_analysis: dict[str, Any]
    ) -> str:
        """Recommend the best target schema based on mappings and content analysis"""
        if not mappings:
            return "FOUNDATIONAL_KB"  # Default fallback

        # Calculate schema scores based on mapping confidence and coverage
        schema_scores = {}

        for mapping in mappings:
            schema = mapping.target_schema
            if schema not in schema_scores:
                schema_scores[schema] = {"total_confidence": 0, "field_count": 0}

            schema_scores[schema]["total_confidence"] += mapping.confidence
            schema_scores[schema]["field_count"] += 1

        # Calculate average confidence for each schema
        for schema, scores in schema_scores.items():
            scores["average_confidence"] = (
                scores["total_confidence"] / scores["field_count"]
            )
            scores["coverage_score"] = min(
                scores["field_count"] / 10, 1.0
            )  # Normalize to 0-1
            scores["final_score"] = (
                scores["average_confidence"] * scores["coverage_score"]
            )

        # Find schema with highest final score
        best_schema = max(schema_scores.items(), key=lambda x: x[1]["final_score"])
        return best_schema[0]

    async def _recommend_chunking_strategy(
        self,
        file_info: dict[str, Any],
        content_analysis: dict[str, Any],
        record_count: int,
    ) -> ChunkingStrategy:
        """Recommend optimal chunking strategy based on data characteristics"""
        file_size_mb = file_info.get("size_bytes", 0) / (1024 * 1024)
        data_type = content_analysis.get("data_classification", "unknown")
        business_domain = content_analysis.get("business_domain", "unknown")

        # Rule-based strategy selection
        if file_info.get("file_type") in [".txt", ".md", ".pdf"]:
            return ChunkingStrategy.DOCUMENT_SECTION
        elif "time" in data_type.lower() or "transaction" in data_type.lower():
            return ChunkingStrategy.TIME_SERIES
        elif (
            business_domain.lower() in ["crm", "sales", "marketing"]
            and record_count > 10000
        ):
            return ChunkingStrategy.RELATIONSHIP_PRESERVING
        elif file_size_mb > 100 or record_count > 50000:
            return ChunkingStrategy.SEMANTIC
        elif (
            "conversation" in data_type.lower() or "communication" in data_type.lower()
        ):
            return ChunkingStrategy.CONTENT_AWARE
        else:
            return ChunkingStrategy.ROW_BASED

    async def _generate_chunk_preview(
        self,
        data: list[dict],
        strategy: ChunkingStrategy,
        content_analysis: dict[str, Any],
    ) -> list[ChunkAnalysis]:
        """Generate preview of how data would be chunked"""
        preview_chunks = []

        try:
            if strategy == ChunkingStrategy.ROW_BASED:
                # Group rows into chunks of 1000
                chunk_size = 1000
                for i in range(
                    0, min(len(data), 5000), chunk_size
                ):  # Preview first 5 chunks
                    chunk_data = data[i : i + chunk_size]
                    chunk = ChunkAnalysis(
                        chunk_id=f"preview_chunk_{i//chunk_size + 1}",
                        chunk_type="data_rows",
                        content_summary=f"Rows {i+1}-{min(i+chunk_size, len(data))} ({len(chunk_data)} records)",
                        business_context=f"Data batch {i//chunk_size + 1}",
                        quality_score=0.8,
                        semantic_coherence=0.7,
                        business_relevance=0.9,
                        relationships=[],
                    )
                    preview_chunks.append(chunk)

            elif strategy == ChunkingStrategy.SEMANTIC:
                # Group by semantic similarity (simplified preview)
                entity_groups = self._group_by_entities(data, content_analysis)
                for i, (entity_type, records) in enumerate(entity_groups.items()):
                    if i >= 5:  # Limit to 5 preview chunks
                        break
                    chunk = ChunkAnalysis(
                        chunk_id=f"semantic_chunk_{i+1}",
                        chunk_type="semantic_group",
                        content_summary=f"{entity_type} related data ({len(records)} records)",
                        business_context=f"Semantic group: {entity_type}",
                        quality_score=0.85,
                        semantic_coherence=0.9,
                        business_relevance=0.8,
                        relationships=[entity_type],
                    )
                    preview_chunks.append(chunk)

            else:
                # Default chunking for other strategies
                chunk_size = 500
                for i in range(
                    0, min(len(data), 2500), chunk_size
                ):  # Preview first 5 chunks
                    chunk_data = data[i : i + chunk_size]
                    chunk = ChunkAnalysis(
                        chunk_id=f"content_chunk_{i//chunk_size + 1}",
                        chunk_type=strategy.value,
                        content_summary=f"Content chunk {i//chunk_size + 1} ({len(chunk_data)} items)",
                        business_context=f"Content group {i//chunk_size + 1}",
                        quality_score=0.75,
                        semantic_coherence=0.8,
                        business_relevance=0.7,
                        relationships=[],
                    )
                    preview_chunks.append(chunk)

        except Exception:
            # Fallback single chunk
            preview_chunks = [
                ChunkAnalysis(
                    chunk_id="fallback_chunk_1",
                    chunk_type="full_dataset",
                    content_summary=f"Complete dataset ({len(data)} records)",
                    business_context="Entire dataset as single chunk",
                    quality_score=0.7,
                    semantic_coherence=0.6,
                    business_relevance=0.8,
                    relationships=[],
                )
            ]

        return preview_chunks

    async def _store_discovery_results(self, result: DataDiscoveryResult):
        """Store discovery results in the staging area"""
        if get_snowflake_connection is None:
            # Skip storage if Snowflake connection is not available
            return

        try:
            async with get_snowflake_connection() as conn:
                async with conn.cursor() as cursor:
                    # Update staged files with discovery results
                    update_query = """
                    UPDATE STAGING_ZONE.STAGED_FILES
                    SET
                        STAGE_STATUS = %s,
                        DETECTED_SCHEMA = %s,
                        SUGGESTED_MAPPINGS = %s,
                        SUGGESTED_TARGET_SCHEMA = %s,
                        CONTENT_ANALYSIS = %s,
                        RECOMMENDED_CHUNK_STRATEGY = %s,
                        CHUNK_PREVIEW = %s,
                        DATA_QUALITY_SCORE = %s,
                        CONFIDENCE_SCORE = %s,
                        VALIDATION_ERRORS = %s,
                        ANALYZED_AT = CURRENT_TIMESTAMP(),
                        UPDATED_AT = CURRENT_TIMESTAMP()
                    WHERE STAGE_ID = %s
                    """

                    await cursor.execute(
                        update_query,
                        (
                            "analyzed",
                            json.dumps(result.detected_schema),
                            json.dumps([asdict(m) for m in result.suggested_mappings]),
                            result.recommended_target_schema,
                            json.dumps(result.content_analysis),
                            result.recommended_chunk_strategy.value,
                            json.dumps([asdict(c) for c in result.chunk_preview]),
                            result.data_quality_score,
                            result.confidence_score,
                            json.dumps(result.validation_errors),
                            result.stage_id,
                        ),
                    )

                    # Store field mappings
                    for mapping in result.suggested_mappings:
                        mapping_query = """
                        INSERT INTO STAGING_ZONE.FIELD_MAPPINGS (
                            MAPPING_ID, STAGE_ID, SOURCE_FIELD_NAME, SUGGESTED_TARGET_FIELD,
                            SUGGESTED_TARGET_SCHEMA, MAPPING_CONFIDENCE, MAPPING_REASONING,
                            MAPPING_STATUS
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        await cursor.execute(
                            mapping_query,
                            (
                                str(uuid.uuid4()),
                                result.stage_id,
                                mapping.source_field,
                                mapping.target_field,
                                mapping.target_schema,
                                mapping.confidence,
                                mapping.reasoning,
                                "suggested",
                            ),
                        )

                    await conn.commit()

        except Exception as e:
            raise Exception(f"Failed to store discovery results: {str(e)}")

    # Helper methods
    def _infer_data_type(self, values: list[Any]) -> str:
        """Infer data type from sample values"""
        if not values:
            return "unknown"

        # Try to determine type from non-null values
        sample_values = [v for v in values if v is not None][:100]

        if not sample_values:
            return "string"

        # Check for numeric types
        try:
            [float(v) for v in sample_values]
            if all(float(v).is_integer() for v in sample_values):
                return "integer"
            else:
                return "float"
        except Exception:
            pass

        # Check for boolean
        bool_values = {str(v).lower() for v in sample_values}
        if bool_values.issubset({"true", "false", "0", "1", "yes", "no"}):
            return "boolean"

        # Check for datetime (simplified check without pandas dependency)
        datetime_indicators = ["date", "time", "created", "updated", "timestamp"]
        for value in sample_values[:10]:
            str_value = str(value).lower()
            if any(indicator in str_value for indicator in datetime_indicators):
                return "datetime"
            # Basic date pattern check
            if len(str_value) >= 8 and any(
                sep in str_value for sep in ["-", "/", ":", " "]
            ):
                return "datetime"

        return "string"

    async def _analyze_field_patterns(
        self, values: list[Any], data_type: str
    ) -> dict[str, Any]:
        """Analyze patterns in field values"""
        pattern_analysis = {
            "common_patterns": [],
            "format_consistency": 0.0,
            "special_characters": False,
            "typical_length": 0,
        }

        if not values:
            return pattern_analysis

        str_values = [str(v) for v in values if v is not None]

        if str_values:
            # Length analysis
            lengths = [len(v) for v in str_values]
            pattern_analysis["typical_length"] = sum(lengths) / len(lengths)

            # Pattern consistency (simplified)
            if data_type == "string":
                # Check for email patterns
                email_count = sum(1 for v in str_values if "@" in v and "." in v)
                if email_count > len(str_values) * 0.5:
                    pattern_analysis["common_patterns"].append("email")

                # Check for phone patterns
                phone_count = sum(
                    1 for v in str_values if any(c.isdigit() for c in v) and len(v) > 7
                )
                if phone_count > len(str_values) * 0.5:
                    pattern_analysis["common_patterns"].append("phone")

                # Check for URL patterns
                url_count = sum(1 for v in str_values if v.startswith(("http", "www")))
                if url_count > len(str_values) * 0.3:
                    pattern_analysis["common_patterns"].append("url")

        return pattern_analysis

    async def _suggest_field_type(
        self, values: list[Any], pattern_analysis: dict
    ) -> str:
        """Suggest improved field type based on analysis"""
        if "email" in pattern_analysis.get("common_patterns", []):
            return "email"
        elif "phone" in pattern_analysis.get("common_patterns", []):
            return "phone"
        elif "url" in pattern_analysis.get("common_patterns", []):
            return "url"
        else:
            return self._infer_data_type(values)

    def _calculate_field_quality_score(
        self,
        null_percentage: float,
        unique_count: int,
        total_count: int,
        pattern_analysis: dict,
    ) -> float:
        """Calculate quality score for a field"""
        # Base score starts at 1.0
        score = 1.0

        # Penalize high null percentage
        if null_percentage > 50:
            score -= 0.4
        elif null_percentage > 20:
            score -= 0.2
        elif null_percentage > 10:
            score -= 0.1

        # Consider uniqueness (but not always good - depends on field type)
        uniqueness_ratio = unique_count / total_count if total_count > 0 else 0
        if uniqueness_ratio < 0.1:  # Very low uniqueness might be bad
            score -= 0.1

        # Bonus for consistent patterns
        if pattern_analysis.get("common_patterns"):
            score += 0.1

        return max(0.0, min(1.0, score))

    def _calculate_data_quality_score(
        self, field_stats: list[FieldStatistics]
    ) -> float:
        """Calculate overall data quality score"""
        if not field_stats:
            return 0.0

        total_score = sum(stat.quality_score for stat in field_stats)
        return total_score / len(field_stats)

    def _calculate_confidence_score(
        self,
        mappings: list[SchemaMapping],
        content_analysis: dict[str, Any],
        data_quality: float,
    ) -> float:
        """Calculate overall confidence in the analysis"""
        if not mappings:
            return 0.3

        # Average mapping confidence
        avg_mapping_confidence = sum(m.confidence for m in mappings) / len(mappings)

        # Content analysis confidence
        content_confidence = content_analysis.get("confidence", 0.5)

        # Data quality contribution
        quality_contribution = data_quality * 0.3

        # Weighted combination
        final_confidence = (
            avg_mapping_confidence * 0.4
            + content_confidence * 0.3
            + quality_contribution
            + 0.1  # Base confidence
        )

        return min(1.0, final_confidence)

    async def _generate_analysis_summary(
        self,
        schema: dict[str, Any],
        mappings: list[SchemaMapping],
        target_schema: str,
        quality_score: float,
    ) -> str:
        """Generate human-readable analysis summary"""
        field_count = len(schema.get("fields", []))
        record_count = schema.get("record_count", 0)
        mapping_count = len(mappings)
        quality_level = self._get_quality_level(quality_score)

        summary = f"""
        Data Analysis Summary:

        • Detected {field_count} fields across {record_count:,} records
        • Overall data quality: {quality_level.value.title()} ({quality_score:.1%})
        • Generated {mapping_count} field mapping suggestions
        • Recommended target schema: {target_schema}

        The analysis shows this data appears to be {target_schema.lower().replace('_', ' ')} related
        with {quality_level.value} data quality suitable for processing.
        """

        return summary.strip()

    def _get_quality_level(self, score: float) -> DataQuality:
        """Convert quality score to quality level"""
        if score >= 0.9:
            return DataQuality.EXCELLENT
        elif score >= 0.7:
            return DataQuality.GOOD
        elif score >= 0.5:
            return DataQuality.FAIR
        elif score >= 0.3:
            return DataQuality.POOR
        else:
            return DataQuality.CRITICAL

    async def _validate_data_quality(
        self, data: list[dict], field_stats: list[FieldStatistics]
    ) -> list[str]:
        """Identify data quality issues and validation errors"""
        errors = []

        # Check for high null rates
        for stat in field_stats:
            if stat.null_percentage > 70:
                errors.append(
                    f"Field '{stat.field_name}' has high null rate ({stat.null_percentage:.1f}%)"
                )

        # Check for data consistency
        if len(data) < 10:
            errors.append("Dataset is very small (less than 10 records)")

        # Check for duplicate headers or unusual field names
        field_names = [stat.field_name for stat in field_stats]
        if len(set(field_names)) != len(field_names):
            errors.append("Duplicate field names detected")

        # Check for entirely empty fields
        empty_fields = [
            stat.field_name for stat in field_stats if stat.null_percentage == 100
        ]
        if empty_fields:
            errors.append(f"Completely empty fields: {', '.join(empty_fields)}")

        return errors

    async def _generate_processing_recommendations(
        self,
        file_info: dict[str, Any],
        quality_score: float,
        chunk_strategy: ChunkingStrategy,
        validation_errors: list[str],
    ) -> dict[str, Any]:
        """Generate recommendations for processing this data"""
        recommendations = {
            "preprocessing_steps": [],
            "chunking_parameters": {},
            "quality_improvements": [],
            "estimated_processing_time": "5-10 minutes",
            "resource_requirements": "standard",
        }

        # Preprocessing recommendations
        if quality_score < 0.7:
            recommendations["preprocessing_steps"].append(
                "Data cleaning and validation"
            )

        if validation_errors:
            recommendations["preprocessing_steps"].append("Address validation errors")

        # Chunking parameters
        if chunk_strategy == ChunkingStrategy.ROW_BASED:
            recommendations["chunking_parameters"] = {
                "chunk_size": 1000,
                "overlap": 0,
                "preserve_relationships": False,
            }
        elif chunk_strategy == ChunkingStrategy.SEMANTIC:
            recommendations["chunking_parameters"] = {
                "chunk_size": 500,
                "overlap": 50,
                "preserve_relationships": True,
            }

        # Resource requirements
        file_size_mb = file_info.get("size_bytes", 0) / (1024 * 1024)
        if file_size_mb > 100:
            recommendations["resource_requirements"] = "high"
            recommendations["estimated_processing_time"] = "30-60 minutes"
        elif file_size_mb > 10:
            recommendations["resource_requirements"] = "medium"
            recommendations["estimated_processing_time"] = "10-20 minutes"

        return recommendations

    def _fallback_content_analysis(
        self, field_names: list[str], sample_data: list[dict]
    ) -> dict[str, Any]:
        """Fallback content analysis when AI analysis fails"""
        # Simple heuristic-based analysis
        business_domain = "unknown"
        data_classification = "structured_data"

        # Check field names for common patterns
        name_text = " ".join(field_names).lower()

        if any(
            term in name_text for term in ["account", "contact", "lead", "opportunity"]
        ):
            business_domain = "crm"
        elif any(term in name_text for term in ["call", "transcript", "recording"]):
            business_domain = "communication"
        elif any(term in name_text for term in ["transaction", "payment", "amount"]):
            business_domain = "financial"

        return {
            "business_domain": business_domain,
            "data_classification": data_classification,
            "key_entities": field_names[:5],
            "field_relationships": {},
            "suggested_use_cases": ["data_analysis", "reporting"],
            "sensitivity_level": "internal",
            "confidence": 0.5,
        }

    def _get_target_schema_candidates(
        self, business_domain: str, content_analysis: dict
    ) -> list[str]:
        """Get likely target schema candidates based on business domain"""
        domain_mapping = {
            "crm": ["SALESFORCE", "HUBSPOT_DATA"],
            "sales": ["SALESFORCE", "HUBSPOT_DATA"],
            "communication": ["GONG_DATA", "AI_MEMORY"],
            "marketing": ["HUBSPOT_DATA", "AI_MEMORY"],
            "financial": ["FOUNDATIONAL_KB"],
            "hr": ["FOUNDATIONAL_KB"],
            "unknown": ["FOUNDATIONAL_KB", "AI_MEMORY"],
        }

        candidates = domain_mapping.get(business_domain.lower(), ["FOUNDATIONAL_KB"])
        return candidates[:3]  # Return top 3 candidates

    async def _find_best_field_match(
        self, field_stat: FieldStatistics, target_fields: list[str], schema_name: str
    ) -> dict[str, Any] | None:
        """Find best matching target field for a source field"""
        field_name = field_stat.field_name.lower()

        # Direct name matching
        for target_field in target_fields:
            if field_name == target_field.lower():
                return {
                    "field": target_field,
                    "confidence": 0.95,
                    "reasoning": f"Direct name match: {field_name} -> {target_field}",
                }

        # Partial matching
        for target_field in target_fields:
            if field_name in target_field.lower() or target_field.lower() in field_name:
                return {
                    "field": target_field,
                    "confidence": 0.8,
                    "reasoning": f"Partial name match: {field_name} -> {target_field}",
                }

        # Semantic matching (simplified)
        semantic_matches = {
            "name": ["name", "title", "label"],
            "email": ["email", "mail", "contact"],
            "phone": ["phone", "mobile", "tel"],
            "id": ["id", "identifier", "key"],
            "date": ["date", "time", "created", "updated"],
        }

        for pattern, keywords in semantic_matches.items():
            if any(keyword in field_name for keyword in keywords):
                for target_field in target_fields:
                    if pattern in target_field.lower():
                        return {
                            "field": target_field,
                            "confidence": 0.7,
                            "reasoning": f"Semantic match: {field_name} -> {target_field}",
                        }

        return None

    def _group_by_entities(
        self, data: list[dict], content_analysis: dict
    ) -> dict[str, list[dict]]:
        """Group data by detected entities (simplified grouping)"""
        groups = {"general": data}  # Simplified - in real implementation, use NER
        return groups

    def _calculate_data_completeness(self, field_stats: list[FieldStatistics]) -> float:
        """Calculate overall data completeness percentage"""
        if not field_stats:
            return 0.0

        total_completeness = sum(100 - stat.null_percentage for stat in field_stats)
        return total_completeness / len(field_stats)
