from typing import Any, Dict
import json
import yaml

from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        extra = "forbid"

    @classmethod
    def from_json(cls, path: str):
        with open(path, "r") as f:
            return cls.parse_obj(json.load(f))

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, "r") as f:
            return cls.parse_obj(yaml.safe_load(f))


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


class PascalBaseModel(BaseModel):
    """Single text recognition holding text and bounding box."""

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True

    def to_dict(self) -> Dict[str, Any]:
        return self.dict(by_alias=True)


class Test(BaseModel):
    a: str
    b: str
