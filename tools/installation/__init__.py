"""
Installation tools for Coqui TTS server.

This package contains tools for model installation and setup.
"""

from .install_portugal_models import install_portugal_models
from .install_portuguese_models import install_portuguese_models
from .sanitize_filenames import sanitize_filename, sanitize_downloads_directory

__all__ = [
    'install_portugal_models',
    'install_portuguese_models',
    'sanitize_filename',
    'sanitize_downloads_directory'
] 