"""Default configuration for the sprite cutter pipeline."""

from dataclasses import dataclass, field


@dataclass
class Config:
    white_threshold: int = 230
    """RGB value above which a pixel is considered 'white' (background)."""

    grid_line_threshold: int = 80
    """Mean brightness below which a row/column counts as a dark separator line."""

    grid_line_min_coverage: float = 0.8
    """Fraction of pixels in a row/col that must be dark for it to be a separator."""

    padding: int = 10
    """Pixels of transparent padding around the cropped sprite."""

    output_size: int = 512
    """Target square size for the final sprite (aspect-ratio preserved, letterboxed)."""

    flood_fill_tolerance: int = 25
    """Color-distance tolerance when flood-filling near-white neighbours."""

    min_sprite_pixels: int = 200
    """Minimum non-transparent pixels for a cell to count as containing a sprite."""

    gap_min_width: int = 8
    """Minimum width (in pixels) of a white band to be recognised as a grid gap."""
