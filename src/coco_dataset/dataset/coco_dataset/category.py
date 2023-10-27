from typing import Optional

from sclearn.utils import BaseModel


class CocoCategory(BaseModel):
    """Coco dataset Category model.

    Attributes:
        id (int): A unique identifier for the category.
        name (str): The name of the category.
        supercategory (Optional[str]): The supercategory of the category. For example,
            one category might be car, while the supercategory might be vehicle.
    """

    id: int
    name: str
    supercategory: Optional[str] = None
