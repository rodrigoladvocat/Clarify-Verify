"""
Pacote Clarify-Verify
"""

import logging
import os


def _configure_logging():
	level_name = os.getenv("CLARIFY_LOG_LEVEL", "INFO").upper()
	level = getattr(logging, level_name, logging.INFO)
	logging.basicConfig(
		level=level,
		format="%(asctime)s %(levelname)s %(name)s - %(message)s"
	)


_configure_logging()
# Módulo principal do Clarify-Verify

