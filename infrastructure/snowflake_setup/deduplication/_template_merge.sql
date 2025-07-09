-- Snowflake MERGE template for canonical-key deduplication
-- Replace <RAW_TABLE>, <STG_TABLE>, <PK_COL>, <UPDATE_COLS>
-- Usage: script generator substitutes tokens then executes.

MERGE INTO <RAW_TABLE> T
USING (
    SELECT * FROM <STG_TABLE>
) S
ON T.<PK_COL> = S.<PK_COL>
WHEN MATCHED AND S._UPDATED_AT_UTC > T._UPDATED_AT_UTC THEN
    UPDATE SET <UPDATE_COLS>
WHEN NOT MATCHED THEN
    INSERT (<UPDATE_COLS>)
    VALUES (<UPDATE_COLS>);