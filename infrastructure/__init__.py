"""基础设施模块"""
from .database import SmartDatabaseMigration
from .resources import resource_manager, ResourceManager
from .embedding import EmbeddingCacheManager
from .events import MemoryEventBus, MemoryEvent, MemoryEventType, get_event_bus, initialize_event_bus, shutdown_event_bus

# 多模态编码器和 LanceDB 存储（可选依赖，导入失败不影响其他功能）
try:
    from .multimodal_encoder import MultimodalEncoder, compute_combined_vector, CLIP_VECTOR_DIM, ZERO_VECTOR
except ImportError:
    MultimodalEncoder = None
    compute_combined_vector = None
    CLIP_VECTOR_DIM = 512
    ZERO_VECTOR = None

try:
    from .lancedb_store import LanceDBVectorStore
except ImportError:
    LanceDBVectorStore = None

__all__ = [
    'SmartDatabaseMigration', 'resource_manager', 'ResourceManager',
    'EmbeddingCacheManager',
    'MemoryEventBus', 'MemoryEvent', 'MemoryEventType',
    'get_event_bus', 'initialize_event_bus', 'shutdown_event_bus',
    'MultimodalEncoder', 'compute_combined_vector', 'CLIP_VECTOR_DIM', 'ZERO_VECTOR',
    'LanceDBVectorStore',
]
