from typing import Optional, Tuple

from sclearn.utils import BaseModel


class CocoAnnotation(BaseModel):
    """Coco dataset Annotation model.

    Attributes:
        id (int): A unique identifier for the annotation.
        image_id (int): The id of the image that this annotation belongs to.
        category_id (int): The id of the category that this annotation belongs to.
        bbox (Tuple[int, int, int, int]): The bounding box of the annotation.
            The format depends on the type value specified in the annotation_type field.
        area (Optional[float]): The area of the annotation.
        segmentation (Optional[list]): The segmentation mask for this annotation.
            The format depends on the type value specified in the annotation_type field.
        iscrowd (Optional[int]): An integer (0 or 1) that specifies whether an
            annotation is a single object or a collection of objects.
    """

    id: int
    image_id: int
    category_id: int
    bbox: Optional[Tuple[float, float, float, float]] = None
    area: Optional[float] = None
    segmentation: Optional[list] = None
    iscrowd: Optional[int] = None
