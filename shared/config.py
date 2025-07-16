from __future__ import annotations

"""Configuration utilities for the Sophia AI backend."""

class Config:
    """Typed configuration loaded from Pulumi ESC."""
    
    @classmethod
    def from_pulumi_esc(cls):
        """Instantiate :class:`Config` using Pulumi ESC values."""
        return cls()