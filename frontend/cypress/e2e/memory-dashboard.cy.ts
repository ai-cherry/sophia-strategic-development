describe('Memory Dashboard', () => {
  beforeEach(() => {
    cy.visit('/memory');
    cy.intercept('GET', '/api/v2/memory/stats', {
      statusCode: 200,
      body: {
        stats: {
          service_status: 'healthy',
          gpu_acceleration: true,
          tiers: {
            L0_gpu_cache: 'Lambda B200',
            L1_redis: 'available',
            L2_weaviate: 'available',
            L3_postgresql: 'available',
          },
          features: {
            gpu_embeddings: true,
            vector_search: true,
            hybrid_search: true,
          },
          performance: {
            embedding_latency: '<50ms',
            search_latency: '<50ms',
            cache_hit_rate: '>80%',
          },
        },
      },
    }).as('getMemoryStats');

    cy.intercept('GET', '/api/v2/metrics/cache', {
      statusCode: 200,
      body: {
        hit_rate: 85.5,
        total_hits: 150000,
        total_misses: 25000,
        memory_usage: '2.3GB',
        connected_clients: 5,
        latency_ms: 12,
      },
    }).as('getCacheMetrics');
  });

  it('should display memory insights tab by default', () => {
    cy.contains('Memory Insights').should('have.class', 'text-blue-400');
    cy.get('input[placeholder*="Search GPU-accelerated memory"]').should('be.visible');
  });

  it('should perform memory search', () => {
    cy.intercept('POST', '/api/v2/memory/search_knowledge', {
      statusCode: 200,
      body: {
        memories: [
          {
            id: '123',
            content: 'Test memory content',
            category: 'test',
            score: 0.95,
            source: 'test/source',
            timestamp: new Date().toISOString(),
            metadata: { test: true },
          },
        ],
      },
    }).as('searchMemory');

    cy.get('input[placeholder*="Search GPU-accelerated memory"]').type('test query');
    cy.contains('button', 'Search').click();

    cy.wait('@searchMemory');
    cy.contains('Test memory content').should('be.visible');
    cy.contains('Score: 95.0%').should('be.visible');
  });

  it('should display redis metrics', () => {
    cy.contains('Redis Metrics').click();
    cy.wait('@getCacheMetrics');

    // Check metrics display
    cy.contains('85.5%').should('be.visible');
    cy.contains('Current Hit Rate').should('be.visible');
    cy.contains('150,000').should('be.visible');
    cy.contains('Total Hits').should('be.visible');
    cy.contains('12ms').should('be.visible');
    cy.contains('Avg Latency').should('be.visible');
  });

  it('should show performance targets', () => {
    cy.contains('Redis Metrics').click();
    cy.contains('Performance Targets').should('be.visible');
    cy.contains('85.5% / 80% target').should('have.class', 'text-green-400');
    cy.contains('12ms / <50ms target').should('have.class', 'text-green-400');
  });

  it('should display system status', () => {
    cy.contains('System Status').click();
    cy.wait('@getMemoryStats');

    // Check tier status
    cy.contains('L0_gpu_cache').should('be.visible');
    cy.contains('L1_redis').should('be.visible');
    cy.contains('L2_weaviate').should('be.visible');
    cy.contains('L3_postgresql').should('be.visible');

    // Check features
    cy.contains('GPU EMBEDDINGS').should('be.visible');
    cy.contains('VECTOR SEARCH').should('be.visible');
    cy.contains('HYBRID SEARCH').should('be.visible');
  });

  it('should have glassmorphism styling', () => {
    cy.get('.glass-card').should('have.length.greaterThan', 0);
    cy.get('.glass-card').first().should('have.css', 'backdrop-filter');
  });

  it('should poll for real-time updates', () => {
    let callCount = 0;
    cy.intercept('GET', '/api/v2/metrics/cache', (req) => {
      callCount++;
      req.reply({
        statusCode: 200,
        body: {
          hit_rate: 85.5 + callCount,
          total_hits: 150000 + callCount * 100,
          total_misses: 25000,
          memory_usage: '2.3GB',
          connected_clients: 5,
          latency_ms: 12,
        },
      });
    }).as('pollCacheMetrics');

    cy.contains('Redis Metrics').click();
    
    // Wait for initial load
    cy.wait('@pollCacheMetrics');
    
    // Wait for second poll (5 seconds)
    cy.wait(5500);
    cy.wait('@pollCacheMetrics');
    
    // Verify the hit rate updated
    cy.contains('86.5%').should('be.visible');
  });
}); 