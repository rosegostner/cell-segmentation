"""
Cell segmentation model wrapper using Cellpose.
"""

from cellpose import models
import numpy as np


class CellSegmentationModel:
    """
    Wrapper around Cellpose for cell segmentation.
    
    Example:
        model = CellSegmentationModel()
        masks, cell_count = model.segment(img)
    """

    def __init__(
        self,
        model_type: str = "cyto3",
        diameter: float = 30.0,
        flow_threshold: float = 0.4,
        cellprob_threshold: float = 0.0,
    ):
        self.model_type = model_type
        self.diameter = diameter
        self.flow_threshold = flow_threshold
        self.cellprob_threshold = cellprob_threshold
        self._model = models.CellposeModel(model_type=model_type)

    def segment(self, img: np.ndarray) -> tuple[np.ndarray, int]:
        """
        Segment cells in an image.

        Args:
            img: Grayscale or RGB image as numpy array.

        Returns:
            masks:      2D array where each cell has a unique integer ID.
            cell_count: Number of detected cells.
        """
        masks, flows, styles = self._model.eval(
            img,
            diameter=self.diameter,
            channels=[0, 0],
            flow_threshold=self.flow_threshold,
            cellprob_threshold=self.cellprob_threshold,
        )

        cell_count = int(masks.max())
        return masks, cell_count
