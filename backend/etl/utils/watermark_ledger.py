from __future__ import annotations

from typing import Any

from shared.utils.modern_stack_cortex_service_core import ModernStackCortexService

LEDGER_TABLE = "OPS_MONITORING.DEDUPE_WATERMARKS"


class WatermarkLedger:
    """Simple helper for reading/writing dedupe watermarks."""

    def __init__(self, cortex: ModernStackCortexService):
        self.cortex = cortex

    async def get(self, source: str, job: str) -> Any | None:
        query = (
            f"SELECT last_watermark FROM {LEDGER_TABLE} "
            "WHERE source_system=%s AND job_name=%s"
        )
        rows = await self.cortex.execute_query(query, (source, job))  # type: ignore[arg-type]
        return rows[0][0] if rows else None

    async def set(self, source: str, job: str, watermark: Any) -> None:
        query = (
            f"MERGE INTO {LEDGER_TABLE} T "
            "USING (SELECT %s AS source_system, %s AS job_name, "
            "%s AS last_watermark) S "
            "ON T.source_system=S.source_system AND T.job_name=S.job_name "
            "WHEN MATCHED THEN UPDATE SET "
            "last_watermark=S.last_watermark, updated_at=CURRENT_TIMESTAMP() "
            "WHEN NOT MATCHED THEN INSERT (source_system, job_name, last_watermark) "
            "VALUES (S.source_system, S.job_name, S.last_watermark)"
        )
        await self.cortex.execute_query(query, (source, job, watermark))  # type: ignore[arg-type]
