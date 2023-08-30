"""Unit-tests for the argspec module."""
import argparse
import dataclasses
from typing import Any, Optional, Sequence, Type

import pytest

from cfgclasses import ConfigClass, MutuallyExclusiveConfigClass, arg, optional
from cfgclasses.argspec import (
    BoolSpecItem,
    ListPositionalSpecItem,
    ListSpecItem,
    OptionalSpecItem,
    PositionalSpecItem,
    Specification,
    SpecificationItem,
    StandardSpecItem,
)


# =============================================================================
# Fixtures used in unit tests
# =============================================================================
@dataclasses.dataclass
class SimpleOptCase(ConfigClass):
    """Case with a simple required option."""

    strfield: str = arg("A simple string field")


simpleoptspec = Specification(
    SimpleOptCase,
    members=[
        StandardSpecItem(
            "strfield",
            help="A simple string field",
            type=str,
        )
    ],
)


@dataclasses.dataclass
class OptionalOptCase(ConfigClass):
    """Case with an optional option."""

    optfield: Optional[str] = optional("An optional string field")


optionaloptspec = Specification(
    OptionalOptCase,
    members=[
        OptionalSpecItem(
            "optfield",
            help="An optional string field",
            type=str,
            default=None,
        )
    ],
)


@dataclasses.dataclass
class ListOptCase(ConfigClass):
    """Case with a list option."""

    # First case has no default or default_factory so is required
    firstlist: list[str] = arg("A list string field")
    # Second case has a default_factory so is optional
    secondlist: list[str] = arg(
        "Another list string field", default_factory=list
    )


listoptspec = Specification(
    ListOptCase,
    members=[
        ListSpecItem(
            "firstlist",
            help="A list string field",
            type=str,
        ),
        ListSpecItem(
            "secondlist",
            help="Another list string field",
            type=str,
            default=[],
        ),
    ],
)


@dataclasses.dataclass
class PositionalOptCase(ConfigClass):
    """Case with a positional option."""

    posfield: str = arg("A positional string field", positional=True)
    poslistfield: list[str] = arg("A positional list field", positional=True)


posoptspec = Specification(
    PositionalOptCase,
    members=[
        PositionalSpecItem(
            "posfield",
            help="A positional string field",
            type=str,
        ),
        ListPositionalSpecItem(
            "poslistfield",
            help="A positional list field",
            type=str,
        ),
    ],
)


# Additional complex case for positional argument to ensure they interact with
# non-positional arguments as expected.
@dataclasses.dataclass
class PositionalAndOptionalCase(ConfigClass):
    """Case with a combination of positional and optional options."""

    strfield: str = arg("A simple string field")
    posfield: str = arg("A positional string field", positional=True)
    intfield: int = arg("An integer field")
    optfield: Optional[str] = optional("An optional string field")
    poslistfield: list[str] = arg(
        "An optional positional list string field",
        positional=True,
        default_factory=list,
    )


posplusoptspec = Specification(
    PositionalAndOptionalCase,
    members=[
        StandardSpecItem(
            "strfield",
            help="A simple string field",
            type=str,
        ),
        PositionalSpecItem(
            "posfield",
            help="A positional string field",
            type=str,
        ),
        StandardSpecItem(
            "intfield",
            help="An integer field",
            type=int,
        ),
        OptionalSpecItem(
            "optfield",
            help="An optional string field",
            type=str,
            default=None,
        ),
        ListPositionalSpecItem(
            "poslistfield",
            help="An optional positional list string field",
            type=str,
            default=[],
        ),
    ],
)


@dataclasses.dataclass
class ChoicesOptCase(ConfigClass):
    """Case with a choices option."""

    choicefield: str = arg(
        "A choice field", choices=["a", "b", "c"], default="a"
    )


choicesoptspec = Specification(
    ChoicesOptCase,
    members=[
        StandardSpecItem(
            "choicefield",
            help="A choice field",
            type=str,
            choices=["a", "b", "c"],
            default="a",
        )
    ],
)


@dataclasses.dataclass
class BooleanOptCase(ConfigClass):
    """Case with a store_true option."""

    boolfield: bool = arg("A boolean field")
    negativeboolfield: bool = arg(
        "An awkward boolean field with a 'True' default",
        default=True,
    )


storetrueoptspec = Specification(
    BooleanOptCase,
    members=[
        BoolSpecItem(
            "boolfield",
            help="A boolean field",
            type=bool,
        ),
        BoolSpecItem(
            "negativeboolfield",
            help="An awkward boolean field with a 'True' default",
            type=bool,
            default=True,
        ),
    ],
)


@dataclasses.dataclass
class OptNameOptCase(ConfigClass):
    """Case with a custom option name."""

    strfield: str = arg("A simple string field", "-c", "--custom-name")


optnameoptspec = Specification(
    OptNameOptCase,
    members=[
        StandardSpecItem(
            "strfield",
            help="A simple string field",
            type=str,
            optnames=["-c", "--custom-name"],
        )
    ],
)


@dataclasses.dataclass
class HasSubGroupCase(ConfigClass):
    """Case with a subspec."""

    subspec: SimpleOptCase = dataclasses.field()


hassubspec = Specification(
    HasSubGroupCase,
    subspecs={"subspec": simpleoptspec},
)


@dataclasses.dataclass
class MutuallyExclusiveGroup(MutuallyExclusiveConfigClass):
    """Example mutually exclusive group."""

    opt_a: int = arg("Option A", default=0)
    opt_b: int = arg("Option B", default=0)


@dataclasses.dataclass
class HasMutuallyExclusiveGroupCase(ConfigClass):
    """Case with a mutually exclusive subspec."""

    subspec: MutuallyExclusiveGroup


hasmutuallyexclusivegroup = Specification(
    HasMutuallyExclusiveGroupCase,
    subspecs={
        "subspec": Specification(
            MutuallyExclusiveGroup,
            members=[
                StandardSpecItem(
                    "opt_a",
                    help="Option A",
                    type=int,
                    default=0,
                ),
                StandardSpecItem(
                    "opt_b",
                    help="Option B",
                    type=int,
                    default=0,
                ),
            ],
        )
    },
)

# =============================================================================
# Test cases
# =============================================================================

test_spec_from_class_cases = {
    "SimpleOptCase": (SimpleOptCase, simpleoptspec),
    "OptionalOptCase": (OptionalOptCase, optionaloptspec),
    "ListOptCase": (ListOptCase, listoptspec),
    "PositionalOptCase": (PositionalOptCase, posoptspec),
    "PositionalAndOptionalCase": (PositionalAndOptionalCase, posplusoptspec),
    "ChoicesOptCase": (ChoicesOptCase, choicesoptspec),
    "BooleanOptCase": (BooleanOptCase, storetrueoptspec),
    "OptNameOptCase": (OptNameOptCase, optnameoptspec),
    "HasSubGroupCase": (HasSubGroupCase, hassubspec),
    "HasMutuallyExclusiveGroupCase": (
        HasMutuallyExclusiveGroupCase,
        hasmutuallyexclusivegroup,
    ),
}


@pytest.mark.parametrize(
    ["configcls", "expectedspec"],
    test_spec_from_class_cases.values(),
    ids=test_spec_from_class_cases.keys(),
)
def test_spec_from_class(
    configcls: Type[ConfigClass], expectedspec: Specification[ConfigClass]
) -> None:
    """
    Test the Specification.from_class function and internally the equivalent for
    SpecificationItem.
    """
    assert Specification.from_class(configcls) == expectedspec


test_specitem_to_kwargs_cases = {
    "required": (
        StandardSpecItem("required", help="is required", type=str),
        {
            "dest": "required",
            "help": "is required",
            "required": True,
            "type": str,
        },
    ),
    "optional": (
        OptionalSpecItem("optional", help="is optional", type=str),
        {
            "dest": "optional",
            "help": "is optional",
            "type": str,
            "required": False,
        },
    ),
    "positional": (
        PositionalSpecItem("pos", help="is positional", type=str),
        {"help": "is positional", "type": str},
    ),
    "choices": (
        StandardSpecItem(
            "choices",
            help="has choices",
            type=str,
            choices=["a", "b", "c"],
        ),
        {
            "dest": "choices",
            "help": "has choices",
            "required": True,
            "choices": ["a", "b", "c"],
            "type": str,
        },
    ),
}


@pytest.mark.parametrize(
    ["specitem", "expectedkwargs"],
    test_specitem_to_kwargs_cases.values(),
    ids=test_specitem_to_kwargs_cases.keys(),
)
def test_specitem_to_kwargs(
    specitem: SpecificationItem, expectedkwargs: dict[str, Any]
) -> None:
    """Test the SpecificationItem.get_kwargs() method."""
    assert specitem.get_kwargs() == expectedkwargs


test_e2e_parser_cases = {
    "simple": (
        simpleoptspec,
        ["--strfield", "test"],
        SimpleOptCase(strfield="test"),
    ),
    # =========================================================================
    # Optional argument tests
    "optional_specified": (
        optionaloptspec,
        ["--optfield", "test"],
        OptionalOptCase(optfield="test"),
    ),
    "optional_not_specified": (
        optionaloptspec,
        [],
        OptionalOptCase(optfield=None),
    ),
    # =========================================================================
    # Positional tests
    "positional": (
        posoptspec,
        ["a", "B1", "B2"],
        PositionalOptCase(posfield="a", poslistfield=["B1", "B2"]),
    ),
    "positional_plus_minimal": (
        posplusoptspec,
        ["a", "--strfield", "test", "--intfield", "100", "X"],
        PositionalAndOptionalCase(
            posfield="a",
            strfield="test",
            intfield=100,
            poslistfield=["X"],
        ),
    ),
    "positional_plus_complete": (
        posplusoptspec,
        [
            "--strfield",
            "test",
            "--intfield",
            "100",
            "--optfield",
            "test",
            "a",
            "X",
            "Y",
            "Z",
        ],
        PositionalAndOptionalCase(
            strfield="test",
            intfield=100,
            optfield="test",
            posfield="a",
            poslistfield=["X", "Y", "Z"],
        ),
    ),
    # =========================================================================
    # Choices tests
    "choices": (
        choicesoptspec,
        ["--choicefield", "a"],
        ChoicesOptCase(choicefield="a"),
    ),
    # =========================================================================
    # Boolean tests
    "store_true_specified": (
        storetrueoptspec,
        ["--boolfield"],
        BooleanOptCase(boolfield=True, negativeboolfield=True),
    ),
    "store_true_not_specified": (
        storetrueoptspec,
        [],
        BooleanOptCase(boolfield=False, negativeboolfield=True),
    ),
    "store_false_specified": (
        storetrueoptspec,
        ["--negativeboolfield"],
        BooleanOptCase(boolfield=False, negativeboolfield=False),
    ),
    # =========================================================================
    # Custom option name tests
    "custom_optname": (
        optnameoptspec,
        ["--custom-name", "test"],
        OptNameOptCase(strfield="test"),
    ),
    "custom_optname_short": (
        optnameoptspec,
        ["-c", "test"],
        OptNameOptCase(strfield="test"),
    ),
    # =========================================================================
    # List tests
    "required_list": (
        listoptspec,
        ["--firstlist", "A", "B", "C"],
        ListOptCase(firstlist=["A", "B", "C"]),
    ),
    "optional_list": (
        listoptspec,
        ["--firstlist", "A", "--secondlist", "B", "C"],
        ListOptCase(firstlist=["A"], secondlist=["B", "C"]),
    ),
    # =========================================================================
    # Subgroup tests
    "has_subgroup": (
        hassubspec,
        ["--strfield", "test"],
        HasSubGroupCase(subspec=SimpleOptCase(strfield="test")),
    ),
    # =========================================================================
    # Mutually exclusive group tests
    "has_mutually_exclusive_group_NULL": (
        hasmutuallyexclusivegroup,
        [],
        HasMutuallyExclusiveGroupCase(
            subspec=MutuallyExclusiveGroup(opt_a=0, opt_b=0)
        ),
    ),
    "has_mutually_exclusive_group_A": (
        hasmutuallyexclusivegroup,
        ["--opt-a", "1"],
        HasMutuallyExclusiveGroupCase(
            subspec=MutuallyExclusiveGroup(opt_a=1, opt_b=0)
        ),
    ),
    "has_mutually_exclusive_group_B": (
        hasmutuallyexclusivegroup,
        ["--opt-b", "1"],
        HasMutuallyExclusiveGroupCase(
            subspec=MutuallyExclusiveGroup(opt_a=0, opt_b=1)
        ),
    ),
}


@pytest.mark.parametrize(
    ["spec", "args", "expectedconfig"],
    test_e2e_parser_cases.values(),
    ids=test_e2e_parser_cases.keys(),
)
def test_e2e_parser(
    spec: Specification[ConfigClass],
    args: Sequence[str],
    expectedconfig: ConfigClass,
) -> None:
    """
    Test the Specification.add_to_parser() and
    Specification.extract_args_from_namespace() methods together.
    """
    parser = argparse.ArgumentParser()
    spec.add_to_parser(parser)
    namespace = parser.parse_args(args)
    assert spec.construct_from_namespace(namespace) == expectedconfig
