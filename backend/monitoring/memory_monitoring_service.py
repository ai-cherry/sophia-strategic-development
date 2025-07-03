
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge

class MemoryMonitoringService:
    def __init__(self):
        self.memory_operations = Counter(
            'sophia_memory_operations_total',
            'Total memory operations',
            ['operation_type', 'memory_tier', 'success']
        )
        
        self.memory_latency = Histogram(
            'sophia_memory_latency_seconds',
            'Memory operation latency',
            ['memory_tier', 'operation_type']
        )
        
        self.learning_effectiveness = Gauge(
            'sophia_learning_effectiveness',
            'Learning effectiveness score',
            ['learning_type']
        )
        