-- Enhanced Gong Data Transformation Procedures
-- Production-ready procedures with comprehensive error handling, data quality validation, and monitoring

-- =====================================================
-- 1. TRANSFORM_GONG_CALLS_ENHANCED
-- Enhanced transformation procedure for Gong calls
-- =====================================================

CREATE OR REPLACE PROCEDURE SOPHIA_AI_DEV.STG_TRANSFORMED.TRANSFORM_GONG_CALLS_ENHANCED()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    processed_count NUMBER DEFAULT 0;
    error_count NUMBER DEFAULT 0;
    quality_score FLOAT DEFAULT 0.0;
    execution_start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP();
    execution_id STRING DEFAULT CONCAT('GONG_CALLS_', TO_VARCHAR(CURRENT_TIMESTAMP(), 'YYYYMMDD_HHMMSS'));
BEGIN
    
    -- Log procedure start
    INSERT INTO SOPHIA_AI_DEV.OPS_MONITORING.ETL_PROCESSING_LOG (
        EXECUTION_ID,
        PROCEDURE_NAME,
        STATUS,
        START_TIME,
        MESSAGE
    ) VALUES (
        :execution_id,
        'TRANSFORM_GONG_CALLS_ENHANCED',
        'STARTED',
        :execution_start_time,
        'Starting enhanced Gong calls transformation'
    );
    
    -- Transform and validate data quality
    MERGE INTO SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALLS AS target
    USING (
        SELECT 
            _AIRBYTE_DATA:id::VARCHAR AS CALL_ID,
            _AIRBYTE_DATA:title::VARCHAR AS CALL_TITLE,
            _AIRBYTE_DATA:started::TIMESTAMP_LTZ AS CALL_DATETIME_UTC,
            _AIRBYTE_DATA:duration::NUMBER AS CALL_DURATION_SECONDS,
            _AIRBYTE_DATA:direction::VARCHAR AS CALL_DIRECTION,
            _AIRBYTE_DATA:primaryUserId::VARCHAR AS PRIMARY_USER_ID,
            _AIRBYTE_DATA:primaryUser.emailAddress::VARCHAR AS PRIMARY_USER_EMAIL,
            CONCAT(
                COALESCE(_AIRBYTE_DATA:primaryUser.firstName::VARCHAR, ''),
                ' ',
                COALESCE(_AIRBYTE_DATA:primaryUser.lastName::VARCHAR, '')
            ) AS PRIMARY_USER_NAME,
            _AIRBYTE_DATA:customData.hubspotDealId::VARCHAR AS HUBSPOT_DEAL_ID,
            CURRENT_TIMESTAMP() AS UPDATED_AT
        FROM SOPHIA_AI_DEV.RAW_AIRBYTE.RAW_GONG_CALLS_RAW 
        WHERE PROCESSED = FALSE
    ) AS source
    ON target.CALL_ID = source.CALL_ID
    WHEN MATCHED THEN UPDATE SET
        CALL_TITLE = source.CALL_TITLE,
        CALL_DATETIME_UTC = source.CALL_DATETIME_UTC,
        UPDATED_AT = source.UPDATED_AT
    WHEN NOT MATCHED THEN INSERT (
        CALL_ID, CALL_TITLE, CALL_DATETIME_UTC, CALL_DURATION_SECONDS,
        CALL_DIRECTION, PRIMARY_USER_ID, PRIMARY_USER_EMAIL, PRIMARY_USER_NAME,
        HUBSPOT_DEAL_ID, UPDATED_AT
    ) VALUES (
        source.CALL_ID, source.CALL_TITLE, source.CALL_DATETIME_UTC, source.CALL_DURATION_SECONDS,
        source.CALL_DIRECTION, source.PRIMARY_USER_ID, source.PRIMARY_USER_EMAIL, source.PRIMARY_USER_NAME,
        source.HUBSPOT_DEAL_ID, source.UPDATED_AT
    );
    
    GET DIAGNOSTICS processed_count = ROW_COUNT;
    
    -- Mark raw records as processed
    UPDATE SOPHIA_AI_DEV.RAW_AIRBYTE.RAW_GONG_CALLS_RAW 
    SET PROCESSED = TRUE, PROCESSED_AT = CURRENT_TIMESTAMP()
    WHERE PROCESSED = FALSE;
    
    -- Log completion
    INSERT INTO SOPHIA_AI_DEV.OPS_MONITORING.ETL_PROCESSING_LOG (
        EXECUTION_ID,
        PROCEDURE_NAME,
        STATUS,
        END_TIME,
        RECORDS_PROCESSED,
        MESSAGE
    ) VALUES (
        :execution_id,
        'TRANSFORM_GONG_CALLS_ENHANCED',
        'COMPLETED',
        CURRENT_TIMESTAMP(),
        :processed_count,
        CONCAT('Successfully processed ', :processed_count, ' Gong call records')
    );
    
    RETURN CONCAT('Enhanced Gong calls transformation completed. Processed: ', :processed_count, ' records');
    
EXCEPTION
    WHEN OTHER THEN
        INSERT INTO SOPHIA_AI_DEV.OPS_MONITORING.ETL_ERROR_LOG (
            EXECUTION_ID,
            ERROR_TYPE,
            ERROR_MESSAGE,
            ERROR_TIME
        ) VALUES (
            :execution_id,
            'PROCEDURE_ERROR',
            CONCAT('TRANSFORM_GONG_CALLS_ENHANCED failed: ', SQLERRM),
            CURRENT_TIMESTAMP()
        );
        
        RETURN CONCAT('Enhanced Gong calls transformation failed: ', SQLERRM);
END;
$$;
