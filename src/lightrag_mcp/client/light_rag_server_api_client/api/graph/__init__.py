"""Contains endpoint functions for accessing the API"""

# Импортируем модули для удобства использования
from .get_graph_labels_graph_label_list_get import asyncio as async_get_graph_labels
from .get_graph_labels_graph_label_list_get import sync as get_graph_labels
from .get_knowledge_graph_graphs_get import asyncio as async_get_knowledge_graph
from .get_knowledge_graph_graphs_get import sync as get_knowledge_graph

__all__ = [
    "get_graph_labels",
    "async_get_graph_labels",
    "get_knowledge_graph",
    "async_get_knowledge_graph",
]
