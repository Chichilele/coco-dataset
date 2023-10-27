"""A simple Flyte example."""

import typing
from flytekit import task, workflow
from coco_dataset import CocoDataset


@task
def say_hello(name: str) -> str:
    m = f"hello {name}! {CocoDataset.__name__}"
    print(m)
    return m


@task
def greeting_length(greeting: str) -> int:
    return len(greeting)


@workflow
def wf(name: str = "union") -> typing.Tuple[str, int]:
    greeting = say_hello(name=name)
    greeting_len = greeting_length(greeting=greeting)
    return greeting, greeting_len


if __name__ == "__main__":
    print(f"Running wf() { wf(name='passengers') }")
