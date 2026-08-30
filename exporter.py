"""
Graph export module for saving NetworkX graphs to various formats.
"""

import json
import logging
from typing import Dict, Any
import networkx as nx
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class GraphExporter:
    """
    Exports NetworkX graphs to various formats (JSON, GraphML, etc.).
    """

    @staticmethod
    def export_to_json(graph: nx.DiGraph, output_path: str) -> None:
        """
        Export a NetworkX directed graph to JSON format.

        Args:
            graph: NetworkX DiGraph object to export
            output_path: Path where to save the JSON file

        Raises:
            IOError: If file cannot be written
        """
        try:
            # Convert graph to JSON-serializable format
            graph_data = GraphExporter._graph_to_dict(graph)

            # Write to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(graph_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Graph exported to {output_path}")
            print(f"✓ Graph saved to {output_path}")

        except IOError as e:
            logger.error(f"Error writing to {output_path}: {e}")
            raise

    @staticmethod
    def _graph_to_dict(graph: nx.DiGraph) -> Dict[str, Any]:
        """
        Convert a NetworkX graph to a JSON-serializable dictionary.

        Args:
            graph: NetworkX DiGraph to convert

        Returns:
            Dictionary representation of the graph
        """
        # Extract nodes with their attributes
        nodes = []
        for node in graph.nodes():
            node_data = {"id": node}
            node_data.update(graph.nodes[node])
            nodes.append(node_data)

        # Extract edges with their attributes
        edges = []
        for source, target in graph.edges():
            edge_data = {"source": source, "target": target}
            edge_attrs = graph.edges[source, target]
            edge_data.update(edge_attrs)
            edges.append(edge_data)

        # Compile full graph data
        graph_dict = {
            "metadata": {
                "nodes_count": graph.number_of_nodes(),
                "edges_count": graph.number_of_edges(),
                "is_directed": graph.is_directed(),
                "density": float(nx.density(graph)),
            },
            "nodes": nodes,
            "edges": edges,
        }

        return graph_dict

    @staticmethod
    def export_to_graphml(graph: nx.DiGraph, output_path: str) -> None:
        """
        Export a NetworkX directed graph to GraphML format.

        Args:
            graph: NetworkX DiGraph object to export
            output_path: Path where to save the GraphML file

        Raises:
            IOError: If file cannot be written
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            nx.write_graphml(graph, output_file)

            logger.info(f"Graph exported to {output_path} (GraphML format)")
            print(f"✓ Graph saved to {output_path}")

        except IOError as e:
            logger.error(f"Error writing to {output_path}: {e}")
            raise

    @staticmethod
    def print_summary(graph: nx.DiGraph, output_path: str) -> None:
        """
        Print a summary of the exported graph.

        Args:
            graph: NetworkX DiGraph object
            output_path: Path where graph was saved
        """
        print("\n" + "=" * 60)
        print("GRAPH EXPORT SUMMARY")
        print("=" * 60)
        print(f"Nodes:    {graph.number_of_nodes()}")
        print(f"Edges:    {graph.number_of_edges()}")
        print(f"Density:  {nx.density(graph):.4f}")
        print(f"Output:   {output_path}")
        print("=" * 60 + "\n")
