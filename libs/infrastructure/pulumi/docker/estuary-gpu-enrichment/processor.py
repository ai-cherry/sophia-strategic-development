#!/usr/bin/env python3
"""Qdrant vector database"""
    processor = GPUEnrichmentProcessor()

    try:
        await processor.initialize()
        await processor.process_stream()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await processor.close()


if __name__ == "__main__":
    asyncio.run(main())
