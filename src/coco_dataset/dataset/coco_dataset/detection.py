from typing import Optional, List

from sclearn.utils import BaseModel


class CocoDetection(BaseModel):
    """Coco dataset Detection model.

    Attributes:
        image_id (int): The id of the image.
        category_id (int): The id of the category.
        bbox (List[int]): The bounding box of the detection.
        score (Optional[float]): The score of the detection.
    """

    image_id: int
    category_id: int
    bbox: List[int]
    score: Optional[float] = None
