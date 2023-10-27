from __future__ import annotations
from typing import List, Tuple, Dict, Optional, Any
import random

from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, Extra, parse_file_as
from loguru import logger

from .annotation import CocoAnnotation
from .category import CocoCategory
from .image import CocoImage
from .info import CocoInfo
from .license import CocoLicense


@dataclass(config=ConfigDict(extra=Extra.forbid, underscore_attrs_are_private=True))
class CocoDataset:
    """Coco dataset model.

    Attributes:
        annotations (List[CocoAnnotation]): List of annotations in the dataset.
        categories (List[CocoCategory]): List of categories (or class) in the dataset.
        images (List[CocoImage]): List of images in the dataset.
        info CocoInfo): Info about the dataset.
        licenses (Optional[CocoLicense]): Info about the licenses of the dataset.
    """

    annotations: List[CocoAnnotation]
    categories: List[CocoCategory]
    images: List[CocoImage]
    info: CocoInfo
    licenses: Optional[List[CocoLicense]] = None

    def __post_init_post_parse__(self):
        self._ims = {im.id: im for im in self.images}
        self._cats = {cat.id: cat for cat in self.categories}
        self._anns = {ann.id: ann for ann in self.annotations}

    @classmethod
    def from_json(cls, path: str):
        return parse_file_as(cls, path)

    def dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Serialize the dataset to a dict."""
        d: Dict[str, Any] = {}
        d["annotations"] = [a.dict(exclude_none=exclude_none) for a in self.annotations]
        d["categories"] = [c.dict(exclude_none=exclude_none) for c in self.categories]
        d["images"] = [im.dict(exclude_none=exclude_none) for im in self.images]
        d["info"] = self.info.dict(exclude_none=exclude_none)
        if self.licenses:
            d["licenses"] = [lc.dict(exclude_none=exclude_none) for lc in self.licenses]
        return d

    def filter_dataset(self, block_list: List[str]) -> CocoDataset:
        """Filter a coco dataset given a block list of outlier images."""
        annotations: List[CocoAnnotation] = []
        images: List[CocoImage] = []
        for ann in self.annotations:
            im = self._ims[ann.image_id]
            cat = self._cats[ann.category_id]
            if im.file_name not in block_list:
                annotations.append(ann)
                images.append(im)
            else:
                logger.info(f"Skipping {im.file_name} of specification {cat.name}.")

        return CocoDataset(
            images=images,
            annotations=annotations,
            categories=self.categories.copy(),
            info=self.info.copy(),
            licenses=self.licenses.copy() if self.licenses else None,
        )

    def merge_classes(self, mappings: Dict[str, str]) -> CocoDataset:
        """Map the class names of a coco dataset."""
        a = set(mappings.keys())
        b = set([cat.name for cat in self.categories])
        diff = a.union(b) - a.intersection(b)
        if diff:
            diff_a = a - b
            diff_b = b - a
            raise ValueError(f"Mappings and dataset don't match: {diff_a}, {diff_b}")

        new_categories: List[CocoCategory] = []
        new_cat_names: List[str] = []  # keep track of new category names
        new_annotations: List[CocoAnnotation] = []
        for ann in self.annotations:
            old_name = self._cats[ann.category_id].name
            new_name = mappings[old_name]

            if new_name in new_cat_names:
                new_category = new_categories[new_cat_names.index(new_name)]
            else:
                new_category = CocoCategory(id=len(new_categories), name=new_name)
                new_categories.append(new_category)
                new_cat_names.append(new_name)

            new_annotations.append(
                CocoAnnotation(
                    id=ann.id, image_id=ann.image_id, category_id=new_category.id
                )
            )
        return CocoDataset(
            annotations=new_annotations,
            categories=new_categories,
            images=self.images.copy(),
            info=self.info.copy(),
            licenses=self.licenses.copy() if self.licenses else None,
        )

    def train_test_split(self, train_ratio=0.8) -> Tuple[CocoDataset, CocoDataset]:
        """Split a coco dataset into train and test sets.

        This preserves the  id of the images, annotations and categories,
        as well at the info, and licenses of the original dataset."""

        random.shuffle(self.annotations)
        cutoff = int(len(self.annotations) * train_ratio)
        train_annotations = self.annotations[:cutoff]
        test_annotations = self.annotations[cutoff:]

        train_images = [self._ims[ann.image_id] for ann in train_annotations]
        test_images = [self._ims[ann.image_id] for ann in test_annotations]

        train_dataset = CocoDataset(
            images=train_images,
            annotations=train_annotations,
            categories=self.categories.copy(),
            info=self.info.copy(),
            licenses=self.licenses.copy() if self.licenses else None,
        )
        test_dataset = CocoDataset(
            images=test_images,
            annotations=test_annotations,
            categories=self.categories.copy(),
            info=self.info.copy(),
            licenses=self.licenses.copy() if self.licenses else None,
        )

        return train_dataset, test_dataset
