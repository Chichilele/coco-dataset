from typing import Optional

from sclearn.utils import BaseModel


class CocoLicense(BaseModel):
    """Coco dataset License model.

    Attributes:
        id (int): A unique identifier for the license.
        name (str): The name of the license.
        url (str): A URL for the license.
    """

    id: int
    name: str
    url: Optional[str] = None
