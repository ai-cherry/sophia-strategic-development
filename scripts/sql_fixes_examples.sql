-- Sophia AI - SQL Fixes Examples
-- This file demonstrates proper SQL practices to address identified issues
-- Including: proper SQL directives, schema qualification, and syntax best practices

--------------------------------------------------------------------------------
-- 1. Proper SQL Directives for Different Database Platforms
--------------------------------------------------------------------------------

-- SQL Server Standard Directives (should be at the top of SQL Server scripts)
SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
SET NOCOUNT ON;

-- PostgreSQL/Snowflake Style Session Settings
-- (When working with PostgreSQL or Snowflake, use these instead)
-- SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
-- SET statement_timeout = 0;
-- SET lock_timeout = 10000;
-- SET client_encoding = 'UTF8';

-- MySQL Style Directives
-- SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
-- SET SESSION sql_mode = 'ANSI,TRADITIONAL';
-- SET NAMES utf8mb4;

--------------------------------------------------------------------------------
-- 2. Schema Qualification Examples
--------------------------------------------------------------------------------

-- INCORRECT: Unqualified table references
-- SELECT * FROM customers WHERE id = 123;
-- INSERT INTO orders (customer_id, order_date) VALUES (123, CURRENT_DATE);

-- CORRECT: Schema-qualified table references
SELECT * FROM dbo.customers WHERE id = 123;
INSERT INTO dbo.orders (customer_id, order_date) VALUES (123, CURRENT_DATE);

-- CORRECT: With explicit schema and aliases
SELECT c.id, c.name, o.order_date
FROM dbo.customers c
JOIN dbo.orders o ON c.id = o.customer_id
WHERE o.order_status = 'Completed';

-- For multi-schema environments, always qualify all tables
SELECT s.subscription_id, p.plan_name
FROM subscription.subscriptions s
JOIN billing.plans p ON s.plan_id = p.plan_id
WHERE s.status = 'active';

--------------------------------------------------------------------------------
-- 3. Proper Parameterization (Examples for Different Platforms)
--------------------------------------------------------------------------------

-- SQL Server Parameter Style
-- EXEC sp_executesql N'SELECT * FROM dbo.customers WHERE status = @status',
--                    N'@status NVARCHAR(50)', @status = 'active';

-- PostgreSQL/Snowflake Parameter Style (In application code)
-- PREPARE customer_query AS
--   SELECT * FROM schema.customers WHERE status = $1;
-- EXECUTE customer_query('active');

-- For non-parameter supporting operations, validate inputs separately
-- Only after validation, use string formatting

-- DDL statements often don't support parameters directly
-- INCORRECT: Creating schema with unsanitized input
-- EXECUTE IMMEDIATE 'CREATE SCHEMA ' || user_input;

-- CORRECT: Validate schema name format before executing DDL
-- This validation would be done in application code, pseudocode:
-- IF schema_name MATCHES '^[a-zA-Z0-9_]+$' THEN
--   EXECUTE 'CREATE SCHEMA ' || schema_name;
-- ELSE
--   RAISE ERROR 'Invalid schema name';
-- END IF;

--------------------------------------------------------------------------------
-- 4. Safe Permissions Management
--------------------------------------------------------------------------------

-- INCORRECT: Overly permissive grants
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO role_user;

-- CORRECT: Grant only necessary permissions
GRANT SELECT ON SCHEMA.table_name TO role_read_only;
GRANT SELECT, INSERT, UPDATE ON SCHEMA.table_name TO role_read_write;
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA.table_name TO role_admin;

-- CORRECT: Role-based permission model
CREATE ROLE app_read_role;
CREATE ROLE app_write_role;
CREATE ROLE app_admin_role;

GRANT USAGE ON SCHEMA app_schema TO app_read_role;
GRANT SELECT ON ALL TABLES IN SCHEMA app_schema TO app_read_role;

GRANT app_read_role TO app_write_role;
GRANT INSERT, UPDATE ON ALL TABLES IN SCHEMA app_schema TO app_write_role;

GRANT app_write_role TO app_admin_role;
GRANT DELETE ON ALL TABLES IN SCHEMA app_schema TO app_admin_role;

-- Grant to specific users
GRANT app_read_role TO user_analyst;
GRANT app_write_role TO user_developer;
GRANT app_admin_role TO user_admin;

--------------------------------------------------------------------------------
-- 5. Correct Transaction Usage
--------------------------------------------------------------------------------

-- Basic transaction pattern
BEGIN TRANSACTION;

INSERT INTO dbo.orders (customer_id, order_date, total_amount)
VALUES (123, CURRENT_DATE, 99.99);

INSERT INTO dbo.order_items (order_id, product_id, quantity, price)
VALUES (SCOPE_IDENTITY(), 456, 1, 99.99);

COMMIT TRANSACTION;

-- With error handling (SQL Server style)
BEGIN TRY
    BEGIN TRANSACTION;
    
    -- Order operations
    INSERT INTO dbo.orders (customer_id, order_date, total_amount)
    VALUES (123, CURRENT_DATE, 99.99);
    
    -- Order items operations
    INSERT INTO dbo.order_items (order_id, product_id, quantity, price)
    VALUES (SCOPE_IDENTITY(), 456, 1, 99.99);
    
    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    
    -- Log error details
    INSERT INTO dbo.error_log (error_number, error_message, error_procedure)
    VALUES (ERROR_NUMBER(), ERROR_MESSAGE(), ERROR_PROCEDURE());
    
    -- Re-throw error
    THROW;
END CATCH;

--------------------------------------------------------------------------------
-- 6. Snowflake-Specific Best Practices
--------------------------------------------------------------------------------

-- Proper warehouse management
USE WAREHOUSE compute_wh;

-- Schema management
USE DATABASE analytics;
USE SCHEMA reporting;

-- Proper table creation with cluster keys
CREATE OR REPLACE TABLE reporting.daily_metrics (
    date_key DATE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT,
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY (date_key);

-- Secure views to enforce row-level security
CREATE OR REPLACE SECURE VIEW reporting.user_metrics AS
SELECT 
    m.date_key,
    m.metric_name,
    m.metric_value,
    m.user_id
FROM reporting.raw_metrics m
WHERE m.user_id = CURRENT_USER() OR IS_ROLE('ADMIN');

-- Proper task creation (Snowflake-specific)
CREATE OR REPLACE TASK reporting.refresh_daily_metrics
    WAREHOUSE = compute_wh
    SCHEDULE = 'USING CRON 0 */4 * * * America/Los_Angeles'
AS
    CALL reporting.sp_refresh_daily_metrics();

--------------------------------------------------------------------------------
-- 7. Proper Table Definitions with Comments
--------------------------------------------------------------------------------

-- Creating a well-structured table with proper constraints and comments
CREATE TABLE dbo.customers (
    customer_id INT IDENTITY(1,1) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    CONSTRAINT chk_status CHECK (status IN ('active', 'inactive', 'suspended'))
);

-- Add column comments
EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Unique identifier for the customer',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'customers',
    @level2type = N'COLUMN', @level2name = N'customer_id';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Customer status (active, inactive, or suspended)',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'customers',
    @level2type = N'COLUMN', @level2name = N'status';

-- Table comment
EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Stores customer account information',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'customers';

--------------------------------------------------------------------------------
-- 8. Stored Procedure Best Practices
--------------------------------------------------------------------------------

-- Properly structured stored procedure with error handling
CREATE OR ALTER PROCEDURE dbo.usp_update_customer_status
    @customer_id INT,
    @new_status VARCHAR(20),
    @updated_by VARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    
    -- Input validation
    IF @customer_id IS NULL OR @new_status IS NULL
    BEGIN
        THROW 50000, 'Customer ID and new status are required', 1;
        RETURN;
    END
    
    IF @new_status NOT IN ('active', 'inactive', 'suspended')
    BEGIN
        THROW 50000, 'Invalid status value. Allowed values: active, inactive, suspended', 1;
        RETURN;
    END
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        -- Update customer status
        UPDATE dbo.customers
        SET status = @new_status,
            updated_at = GETDATE()
        WHERE customer_id = @customer_id;
        
        -- If no rows affected, customer doesn't exist
        IF @@ROWCOUNT = 0
        BEGIN
            THROW 50000, 'Customer not found', 1;
        END
        
        -- Log the status change
        INSERT INTO dbo.customer_status_history
            (customer_id, old_status, new_status, changed_at, changed_by)
        SELECT
            @customer_id,
            status,
            @new_status,
            GETDATE(),
            @updated_by
        FROM dbo.customers
        WHERE customer_id = @customer_id;
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        
        -- Log the error
        INSERT INTO dbo.error_log
            (error_number, error_message, error_procedure, error_line, created_at)
        VALUES
            (ERROR_NUMBER(), ERROR_MESSAGE(), ERROR_PROCEDURE(), ERROR_LINE(), GETDATE());
        
        -- Re-throw the error
        THROW;
    END CATCH;
END;

--------------------------------------------------------------------------------
-- 9. Index Creation Best Practices
--------------------------------------------------------------------------------

-- Proper index creation with include columns and fill factor
CREATE NONCLUSTERED INDEX IX_customers_email
ON dbo.customers (email)
INCLUDE (first_name, last_name, status)
WITH (FILLFACTOR = 90, ONLINE = ON);

-- Create indexes for foreign keys
CREATE NONCLUSTERED INDEX IX_orders_customer_id
ON dbo.orders (customer_id);

-- Composite index for common query patterns
CREATE NONCLUSTERED INDEX IX_orders_status_date
ON dbo.orders (status, order_date DESC)
INCLUDE (customer_id, total_amount);

--------------------------------------------------------------------------------
-- 10. Data Migration Best Practices
--------------------------------------------------------------------------------

-- Safe data migration pattern with temp table
-- 1. Create temp table with new structure
CREATE TABLE dbo.customers_new (
    customer_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    created_at DATETIME2 NOT NULL,
    updated_at DATETIME2 NOT NULL,
    status VARCHAR(20) NOT NULL,
    -- New column
    preferred_language VARCHAR(10) NOT NULL DEFAULT 'en'
);

-- 2. Copy data from old table to new table
INSERT INTO dbo.customers_new (
    customer_id, first_name, last_name, email, 
    phone, created_at, updated_at, status
)
SELECT 
    customer_id, first_name, last_name, email, 
    phone, created_at, updated_at, status
FROM dbo.customers;

-- 3. Rename tables to swap them (SQL Server)
EXEC sp_rename 'dbo.customers', 'customers_old';
EXEC sp_rename 'dbo.customers_new', 'customers';

-- 4. Create necessary indexes on new table
CREATE UNIQUE NONCLUSTERED INDEX IX_customers_email
ON dbo.customers (email);

-- 5. Verify data and drop old table when safe
-- SELECT COUNT(*) FROM dbo.customers_old;
-- SELECT COUNT(*) FROM dbo.customers;
-- DROP TABLE dbo.customers_old;