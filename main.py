#!/usr/bin/env python3
"""
Wikipedia Graph Scraper - Extract links and build a graph from web pages.

Main entry point for the application.
Accepts a URL as input, scrapes all links, and exports as a graph in JSON format.
"""

import argparse
import logging
import sys
import time
from pathlib import Path

from scraper import WebScraper
from graph_builder import GraphBuilder
from exporter import GraphExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract links from a website and build a graph structure.",
        epilog="Example: python main.py --url https://en.wikipedia.org/wiki/Python --depth 2",
    )

    parser.add_argument(
        "--url",
        required=True,
        type=str,
        help="Starting URL to scrape (e.g., https://en.wikipedia.org/wiki/Python)",
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Maximum traversal depth (default: 2)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="graph.json",
        help="Output file path for the graph (default: graph.json)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="HTTP request timeout in seconds (default: 10)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging (debug level)",
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("Wikipedia Graph Scraper Started")
    logger.info("=" * 60)
    logger.info(f"URL: {args.url}")
    logger.info(f"Depth: {args.depth}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Timeout: {args.timeout}s")

    try:
        start_time = time.time()

        # Initialize scraper
        scraper = WebScraper(timeout=args.timeout)

        # Build graph using BFS
        builder = GraphBuilder(scraper)
        graph = builder.build_graph(start_url=args.url, max_depth=args.depth)

        # Export to JSON
        exporter = GraphExporter()
        exporter.export_to_json(graph, args.output)
        exporter.print_summary(graph, args.output)

        # Clean up
        scraper.close()

        elapsed_time = time.time() - start_time
        logger.info(f"Completed in {elapsed_time:.2f} seconds")

        return 0

    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())