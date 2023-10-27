from typing import Optional

from sclearn.utils import BaseModel


class CocoImage(BaseModel):
    """Coco dataset Image model.

    Attributes:
        id (int): A unique identifier for the image.
            Used as mapping in the annotations array.
        file_name (str): The image file name.
        coco_url (str): The location of the image.
        width (Optional[int]): The width of the image.
        height (Optional[int]): The height of the image.
        date_captured (Optional[str]): the date and time the image was captured.
        license (Optional[int]): Maps to the license array.
    """

    id: int
    file_name: str
    coco_url: str
    width: Optional[int] = None
    height: Optional[int] = None
    date_captured: Optional[str] = None
    license: Optional[int] = None
