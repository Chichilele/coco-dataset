from typing import Optional

from sclearn.utils import BaseModel


class CocoInfo(BaseModel):
    """Coco dataset Info model.

    Attributes:
        description (str): A description of the dataset.
        date_created (str): The date the dataset was released.
        version (Optional[str]): The version of the dataset.
        url (Optional[str]): A URL for the dataset.
        year (Optional[int]): The year the dataset was released.
        contributor (Optional[str]): The person/people who created the dataset.
    """

    description: str
    date_created: str
    version: str
    url: Optional[str] = None
    year: Optional[int] = None
    contributor: Optional[str] = None
