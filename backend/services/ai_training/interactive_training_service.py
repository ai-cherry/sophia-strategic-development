# The connection should be closed by the connection pool manager
# await self.db_connector.release_connection(conn)

async def get_training_feed(self, limit: int = 50) -> list[dict]:
    """
    Retrieves the most recent authoritative knowledge submissions for the live feed.
    """
    logger.info(f"Fetching the last {limit} training submissions for the dashboard feed.")
    try:
        conn = await self.db_connector.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT ak.topic, ak.content, u.username, ak.user_impact_score, ak.last_updated_at
            FROM payready_core_sql.authoritative_knowledge ak
            JOIN payready_core_sql.users u ON ak.source_user_id = u.user_id
            ORDER BY ak.last_updated_at DESC
            LIMIT %s;
        """
        cursor.execute(query, (limit,))
        feed_items = cursor.fetchall()
        
        # Convert list of tuples to list of dicts for API response
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in feed_items]
        
    except Exception as e:
        logger.exception(f"Failed to fetch training feed: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()

async def get_knowledge_gaps(self) -> list[dict]:
    """
    Identifies potential knowledge gaps.
    
    This is a placeholder for a more sophisticated analysis. A real implementation
    would analyze user query logs against the authoritative_knowledge table
    to find frequently asked topics with no defined knowledge.
    """
    logger.info("Analyzing for knowledge gaps.")
    # Mock implementation: Returns predefined topics that need definitions.
    gaps = [
        {"topic": "Q4 Sales Strategy", "queries_missed": 15, "priority": "High"},
        {"topic": "Project Phoenix Budget", "queries_missed": 12, "priority": "High"},
        {"topic": "Competitor X Pricing Model", "queries_missed": 9, "priority": "Medium"},
        {"topic": "New Employee Onboarding Process", "queries_missed": 5, "priority": "Low"},
    ]
    return gaps

async def manage_knowledge(self, knowledge_id: str, action: str, content: str = None) -> dict:
    """
    Allows a CEO/admin to manage a piece of authoritative knowledge.
    Actions: 'update' or 'delete'.
    """
    logger.info(f"Performing action '{action}' on knowledge ID '{knowledge_id}'")
    if action not in ['update', 'delete']:
        return {"status": "error", "message": "Invalid action."}
        
    try:
        conn = await self.db_connector.get_connection()
        cursor = conn.cursor()
        
        if action == 'delete':
            cursor.execute(
                "DELETE FROM payready_core_sql.authoritative_knowledge WHERE knowledge_id = %s",
                (knowledge_id,)
            )
            message = f"Successfully deleted knowledge ID '{knowledge_id}'."
        
        if action == 'update':
            if not content:
                return {"status": "error", "message": "Content is required for update."}
            cursor.execute(
                "UPDATE payready_core_sql.authoritative_knowledge SET content = %s, last_updated_at = CURRENT_TIMESTAMP() WHERE knowledge_id = %s",
                (content, knowledge_id)
            )
            message = f"Successfully updated knowledge ID '{knowledge_id}'."
        
        return {"status": "success", "message": message}
        
    except Exception as e:
        logger.exception(f"Failed to perform '{action}' on knowledge ID '{knowledge_id}': {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if 'cursor' in locals():
            cursor.close() 
    async def get_training_feed(self, limit: int = 50) -> list[dict]:
        """
        Retrieves the most recent authoritative knowledge submissions for the live feed.
        """
        logger.info(f"Fetching the last {limit} training submissions for the dashboard feed.")
        try:
            conn = await self.db_connector.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT ak.topic, ak.content, u.username, ak.user_impact_score, ak.last_updated_at
                FROM payready_core_sql.authoritative_knowledge ak
                JOIN payready_core_sql.users u ON ak.source_user_id = u.user_id
                ORDER BY ak.last_updated_at DESC
                LIMIT %s;
            """
            cursor.execute(query, (limit,))
            feed_items = cursor.fetchall()
            
            # Convert list of tuples to list of dicts for API response
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in feed_items]
            
        except Exception as e:
            logger.exception(f"Failed to fetch training feed: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()

    async def get_knowledge_gaps(self) -> list[dict]:
        """
        Identifies potential knowledge gaps.
        
        This is a placeholder for a more sophisticated analysis. A real implementation
        would analyze user query logs against the authoritative_knowledge table
        to find frequently asked topics with no defined knowledge.
        """
        logger.info("Analyzing for knowledge gaps.")
        # Mock implementation: Returns predefined topics that need definitions.
        gaps = [
            {"topic": "Q4 Sales Strategy", "queries_missed": 15, "priority": "High"},
            {"topic": "Project Phoenix Budget", "queries_missed": 12, "priority": "High"},
            {"topic": "Competitor X Pricing Model", "queries_missed": 9, "priority": "Medium"},
            {"topic": "New Employee Onboarding Process", "queries_missed": 5, "priority": "Low"},
        ]
        return gaps

    async def manage_knowledge(self, knowledge_id: str, action: str, content: str = None) -> dict:
        """
        Allows a CEO/admin to manage a piece of authoritative knowledge.
        Actions: 'update' or 'delete'.
        """
        logger.info(f"Performing action '{action}' on knowledge ID '{knowledge_id}'")
        if action not in ['update', 'delete']:
            return {"status": "error", "message": "Invalid action."}
            
        try:
            conn = await self.db_connector.get_connection()
            cursor = conn.cursor()
            
            if action == 'delete':
                cursor.execute(
                    "DELETE FROM payready_core_sql.authoritative_knowledge WHERE knowledge_id = %s",
                    (knowledge_id,)
                )
                message = f"Successfully deleted knowledge ID '{knowledge_id}'."
            
            if action == 'update':
                if not content:
                    return {"status": "error", "message": "Content is required for update."}
                cursor.execute(
                    "UPDATE payready_core_sql.authoritative_knowledge SET content = %s, last_updated_at = CURRENT_TIMESTAMP() WHERE knowledge_id = %s",
                    (content, knowledge_id)
                )
                message = f"Successfully updated knowledge ID '{knowledge_id}'."
            
            return {"status": "success", "message": message}
            
        except Exception as e:
            logger.exception(f"Failed to perform '{action}' on knowledge ID '{knowledge_id}': {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if 'cursor' in locals():
                cursor.close()
