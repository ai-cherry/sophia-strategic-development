"""Qdrant vector database"""
        self.logger.info("AI Memory server V3 shutting down...")

        # Close connections
        if self.memory_service:
            await self.memory_service.close()

        self.logger.info("AI Memory server V3 stopped")

# Create and run server
if __name__ == "__main__":
    import asyncio

    async def main():
        server = AIMemoryServerV2()
        await server.run()

    asyncio.run(main())
