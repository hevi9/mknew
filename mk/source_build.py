from __future__ import annotations

from typing import Iterable, Mapping, Type

import strictyaml  # type: ignore

from .bases import Runnable
from .location import Location
from .make_copy import Copy
from .make_move import Move
from .make_remove import Remove
from .make_shell import Shell
from .make_use import Use
from .source import Source

MAKE_ITEM_MAP = {
    "shell": Shell,
    "use": Use,
    "remove": Remove,
    "copy": Copy,
    "move": Move,
}


def make_source_from_dict(item: dict, location: Location) -> Source:
    """ """
    source = Source(
        name=item["source"],
        control=item,
        location=location,
    )
    make_list = item["make"]
    for make_item in make_list:
        if isinstance(make_item, str):
            make_item = {"shell": make_item}
        elif isinstance(make_item, dict):
            pass
        else:
            raise TypeError(f"Invalid make item type {type(make_item)}")
        make_type = make_item.keys() & MAKE_ITEM_MAP.keys()
        if len(make_type) < 1:
            raise ValueError(
                f"""Unknown make type in item {make_item} in {location},
                available make types {MAKE_ITEM_MAP.keys()}"""
            )
        if len(make_type) > 1:
            raise ValueError(f"Conflicting make types {make_type}")
        make_type = make_type.pop()
        source.make.append(MAKE_ITEM_MAP[make_type](source, make_item))  # type: ignore

    return source


def make_sources_from_file_yaml(location: Location) -> Iterable[Source]:
    with location.path_abs.open() as fo:
        text = fo.read()
        data = strictyaml.load(text, label=str(location.path_abs)).data
        if not isinstance(data, list):
            raise TypeError(f"not a list {data}")
        for item in data:
            yield make_source_from_dict(item, location)
