"""
Graph building module using NetworkX for constructing URL graphs via BFS.
"""

import networkx as nx
import logging
from collections import deque
from typing import Set, Tuple
from urllib.parse import urlparse
from scraper import WebScraper

# Configure logging
logger = logging.getLogger(__name__)


class GraphBuilder:
    """
    Builds a directed graph of URLs using breadth-first search (BFS).
    """

    def __init__(self, scraper: WebScraper):
        """
        Initialize the graph builder.

        Args:
            scraper: WebScraper instance for fetching and extracting links
        """
        self.scraper = scraper
        self.visited_urls: Set[str] = set()
        self.graph = nx.DiGraph()

    def build_graph(self, start_url: str, max_depth: int = 2) -> nx.DiGraph:
        """
        Build a graph of URLs using BFS from a starting URL.

        Args:
            start_url: Starting URL for the graph
            max_depth: Maximum traversal depth (default: 2)

        Returns:
            NetworkX DiGraph object containing the discovered URLs and links
        """
        self.graph = nx.DiGraph()
        self.visited_urls = set()

        # BFS queue: (url, current_depth)
        queue = deque([(start_url, 0)])
        self.visited_urls.add(start_url)

        # Add starting node
        self.graph.add_node(start_url, depth=0, label=self._get_url_label(start_url))

        logger.info(f"Starting BFS from {start_url} with max_depth={max_depth}")

        while queue:
            current_url, current_depth = queue.popleft()

            # Stop if max depth reached
            if current_depth >= max_depth:
                logger.debug(f"Max depth {max_depth} reached for {current_url}")
                continue

            logger.info(f"Processing [{current_depth}] {current_url}")

            # Fetch page and extract links
            html = self.scraper.fetch_page(current_url)
            if html is None:
                logger.warning(f"Skipping {current_url} - failed to fetch")
                continue

            links = self.scraper.extract_links(html, current_url)
            logger.debug(f"Found {len(links)} links on {current_url}")

            # Process each discovered link
            for link in links:
                # Add link as node if not visited
                if link not in self.visited_urls:
                    self.visited_urls.add(link)
                    next_depth = current_depth + 1
                    self.graph.add_node(
                        link, depth=next_depth, label=self._get_url_label(link)
                    )
                    logger.debug(f"Added node: {link} (depth={next_depth})")

                    # Add to queue if depth allows further traversal
                    if next_depth < max_depth:
                        queue.append((link, next_depth))

                # Add edge from current URL to discovered link
                self.graph.add_edge(current_url, link)

        logger.info(
            f"BFS completed. Graph has {self.graph.number_of_nodes()} nodes"
            f" and {self.graph.number_of_edges()} edges"
        )

        return self.graph

    @staticmethod
    def _get_url_label(url: str) -> str:
        """
        Generate a label for a URL (extract domain and path).

        Args:
            url: URL to label

        Returns:
            Human-readable label for the URL
        """
        try:
            parsed = urlparse(url)
            path = parsed.path.split("/")[-1] or parsed.netloc
            return path[:50]  # Truncate to 50 chars
        except Exception:
            return url[:50]

    def get_graph_stats(self) -> dict:
        """
        Get statistics about the current graph.

        Returns:
            Dictionary with graph statistics
        """
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "is_directed": self.graph.is_directed(),
        }
