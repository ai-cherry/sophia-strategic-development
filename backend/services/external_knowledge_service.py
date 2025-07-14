"""Qdrant vector database"""
        trends = await self.get_trending_topics()

        for trend in trends[:5]:  # Top 5 trends
            # Skip if not relevant to business
            if any(
                skip in trend["topic"].lower()
                for skip in ["celebrity", "sports", "entertainment"]
            ):
                continue

            # Enrich with this trending topic
            await self.enrich_query_with_external(
                query=trend["topic"], sources=["x", "news"]
            )

            # Don't overwhelm APIs
            await asyncio.sleep(2)

        self.logger.info(f"Auto-enriched {len(trends)} trending topics")
