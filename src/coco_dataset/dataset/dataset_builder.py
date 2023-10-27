"""Dataset builder class to query the database, and create a dataset."""
from typing import List, Optional, Tuple
from datetime import date

import pandas as pd
from tqdm import tqdm

from .coco_dataset.dataset import CocoDataset
from .coco_dataset.annotation import CocoAnnotation
from .coco_dataset.category import CocoCategory
from .coco_dataset.image import CocoImage
from .coco_dataset.info import CocoInfo

from .s3_path_parser import ImageS3PathParser


class DfToCocoBuilder:
    """Dataset builder class to build a Coco dataset from a pandas dataframe."""

    def __init__(
        self, dataset_name: str, dataframe: pd.DataFrame, path_parser: ImageS3PathParser
    ):
        """
        Args:
            dataset_name (str): name of the dataset
            dataframe (pd.DataFrame): dataframe to build the dataset from
            path_parser (ImageS3PathParser): parser to get image s3 pathes
        """
        self.df = dataframe
        self.parser = path_parser
        self._check_df_fields()

        self.categories_builder: CategoriesBuilder = CategoriesBuilder()
        self.images_builder: ImagesBuilder = ImagesBuilder()
        self.annotations_builder: AnnotationsBuilder = AnnotationsBuilder()
        self.info = CocoInfo(
            description=dataset_name,
            date_created=str(date.today()),
            version="1.0.0",
        )

    def _check_df_fields(self):
        """Check that the dataframe has all the requires fields"""
        fields = set(self.df.columns)
        expected = {"BucketRegion", "S3Bucket", "CaptureFolderId", "SpecificationClass"}
        missing = expected - fields
        if missing:
            formatted_missing = sorted(list(missing))
            raise ValueError(f"Missing fields: {formatted_missing}")

    def build(self) -> CocoDataset:
        """Builds a Cocodataset."""
        for i, row in tqdm(self.df.iterrows(), total=self.df.shape[0]):
            for image_url in self.parser.get_image_url(row["CaptureFolderId"]):
                file_name = self._get_filename(image_url)
                cat_id = self.categories_builder.get_or_add_id(
                    row["SpecificationClass"]
                )
                date_str = str(row["CaptureDate"])
                img_id = self.images_builder.get_or_add_id(
                    file_name, coco_url=image_url, date_captured=date_str
                )
                self.annotations_builder.get_or_add_id(
                    image_id=img_id, category_id=cat_id
                )

        return CocoDataset(
            images=self.images_builder.images,
            categories=self.categories_builder.categories,
            annotations=self.annotations_builder.annotations,
            info=self.info,
        )

    def _get_filename(self, image_url: str) -> str:
        """Gets the filename from the image url.

        Expected format: s3://<bucket>/<path>/<to>/<image>.JPG.
        Replaces ` ` with `_` and `/` with `__`."""
        image_url = image_url.replace("s3://", "").replace(" ", "_")
        name_bits = image_url.split("/")
        return "__".join(name_bits[1:]).replace(".JPG", ".jpg")


class ImagesBuilder:
    """Images builder class to build the images of a dataset."""

    images: List[CocoImage]

    def __init__(self) -> None:
        self.images: List[CocoImage] = list()

    def get_or_add_id(
        self,
        file_name: str,
        coco_url: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        date_captured: Optional[str] = None,
        license: Optional[int] = None,
    ) -> int:
        """Get image from the Coco Images. Adds a new image if needed."""
        matches = [c for c in self.images if c.file_name == file_name]

        if len(matches) > 1:
            raise ValueError(f"Image name '{file_name}' has multiple matches!")
        if len(matches) == 1:
            return matches[0].id
        if len(matches) == 0:
            return self._add_image(
                file_name,
                coco_url,
                width,
                height,
                date_captured,
                license,
            )
        else:
            raise Exception(
                f"Error matching Coco Images from {len(matches)} images "
                f"error trying to match name: '{file_name}'!!"
            )

    def _add_image(
        self,
        file_name: str,
        coco_url: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        date_captured: Optional[str] = None,
        license: Optional[int] = None,
    ) -> int:
        """Add an Image, setting the index incrementally."""
        image_id = 1 + max([c.id for c in self.images]) if self.images else 0

        new_image = CocoImage(
            id=image_id,
            file_name=file_name,
            coco_url=coco_url,
            width=width,
            height=height,
            date_captured=date_captured,
            license=license,
        )
        self.images.append(new_image)

        return image_id


class CategoriesBuilder:
    """Categories builder class to build the categories of a dataset."""

    categories: List[CocoCategory]

    def __init__(self) -> None:
        self.categories: List[CocoCategory] = list()

    def get_or_add_id(self, name: str, supercategory: Optional[str] = None) -> int:
        """Get category from the Coco Categories. Adds a new category if needed."""
        matches = [c for c in self.categories if c.name == name]

        if len(matches) > 1:
            raise ValueError(f"Category name '{name}' has multiple matches!")
        if len(matches) == 1:
            return matches[0].id
        if len(matches) == 0:
            return self._add_category(name, supercategory)
        else:
            raise Exception(
                f"Error matching Coco categories from {len(matches)} categories "
                f"error trying to match name: '{name}'!!"
            )

    def _add_category(self, name, supercategory) -> int:
        """Add a category, setting the index incrementally."""
        cat_id = 1 + max([c.id for c in self.categories]) if self.categories else 0
        new_cat = CocoCategory(id=cat_id, name=name, supercategory=supercategory)
        self.categories.append(new_cat)

        return cat_id


class AnnotationsBuilder:
    """Annotations builder class to build the annotations of a dataset."""

    annotations: List[CocoAnnotation]

    def __init__(self) -> None:
        self.annotations: List[CocoAnnotation] = list()

    def get_or_add_id(
        self,
        image_id: int,
        category_id: int,
        bbox: Optional[Tuple[float, float, float, float]] = None,
        area: Optional[float] = None,
        segmentation: Optional[list] = None,
        iscrowd: Optional[int] = None,
    ) -> int:
        """Add an Annotation, setting the index incrementally."""
        ann_id = 1 + max([an.id for an in self.annotations]) if self.annotations else 0

        new_annotation = CocoAnnotation(
            id=ann_id,
            image_id=image_id,
            category_id=category_id,
            bbox=bbox,
            area=area,
            segmentation=segmentation,
            iscrowd=iscrowd,
        )

        self.annotations.append(new_annotation)

        return ann_id
