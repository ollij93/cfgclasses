"""Unit-tests for the argspec module."""
import argparse
import dataclasses
from typing import Any, Optional, Sequence, Type

import pytest

from cfgclasses import (
    ConfigClass,
    choices,
    mutually_exclusive_group,
    optional,
    positional,
    simple,
    store_true,
)
from cfgclasses.argspec import ArgGroup, ArgOpts, ArgSpec, ArgSubGroup


# =============================================================================
# Fixtures used in unit tests
# =============================================================================
@dataclasses.dataclass
class SimpleOptCase(ConfigClass):
    """Case with a simple required option."""

    strfield: str = simple("A simple string field")


simpleoptgroup = ArgGroup(
    members=[
        ArgSpec(
            "strfield",
            "A simple string field",
            ["--strfield"],
            ArgOpts(required=True, type=str),
        )
    ]
)


@dataclasses.dataclass
class OptionalOptCase(ConfigClass):
    """Case with an optional option."""

    optfield: Optional[str] = optional("An optional string field")


optionaloptgroup = ArgGroup(
    members=[
        ArgSpec(
            "optfield",
            "An optional string field",
            ["--optfield"],
            ArgOpts(default=None, required=False, type=str),
        )
    ]
)


@dataclasses.dataclass
class PositionalOptCase(ConfigClass):
    """Case with a positional option."""

    posfield: str = positional("A positional string field")
    poslistfield: list[str] = positional("A positional list field")


posoptgroup = ArgGroup(
    members=[
        ArgSpec(
            "posfield",
            "A positional string field",
            ["posfield"],
            ArgOpts(type=str),
        ),
        ArgSpec(
            "poslistfield",
            "A positional list field",
            ["poslistfield"],
            ArgOpts(type=str, nargs="+"),
        ),
    ]
)


# Additional complex case for positional argument to ensure they interact with
# non-positional arguments as expected.
@dataclasses.dataclass
class PositionalAndOptionalCase(ConfigClass):
    """Case with a combination of positional and optional options."""

    strfield: str = simple("A simple string field")
    posfield: str = positional("A positional string field")
    intfield: int = simple("An integer field")
    optfield: Optional[str] = optional("An optional string field")
    poslistfield: list[str] = positional(
        "An optional positional list string field",
        nargs="*",
        default_factory=list,
    )


posplusoptgroup = ArgGroup(
    members=[
        ArgSpec(
            "strfield",
            "A simple string field",
            ["--strfield"],
            ArgOpts(required=True, type=str),
        ),
        ArgSpec(
            "posfield",
            "A positional string field",
            ["posfield"],
            ArgOpts(type=str),
        ),
        ArgSpec(
            "intfield",
            "An integer field",
            ["--intfield"],
            ArgOpts(required=True, type=int),
        ),
        ArgSpec(
            "optfield",
            "An optional string field",
            ["--optfield"],
            ArgOpts(default=None, required=False, type=str),
        ),
        ArgSpec(
            "poslistfield",
            "An optional positional list string field",
            ["poslistfield"],
            ArgOpts(type=str, nargs="*", default=[]),
        ),
    ]
)


@dataclasses.dataclass
class ChoicesOptCase(ConfigClass):
    """Case with a choices option."""

    choicefield: str = choices("A choice field", ["a", "b", "c"], default="a")


choicesoptgroup = ArgGroup(
    members=[
        ArgSpec(
            "choicefield",
            "A choice field",
            ["--choicefield"],
            ArgOpts(type=str, choices=["a", "b", "c"], default="a"),
        )
    ]
)


@dataclasses.dataclass
class StoreTrueOptCase(ConfigClass):
    """Case with a store_true option."""

    boolfield: bool = store_true("A boolean field")


storetrueoptgroup = ArgGroup(
    members=[
        ArgSpec(
            "boolfield",
            "A boolean field",
            ["--boolfield"],
            ArgOpts(action="store_true", default=False),
        )
    ]
)


@dataclasses.dataclass
class OptNameOptCase(ConfigClass):
    """Case with a custom option name."""

    strfield: str = simple(
        "A simple string field", optnames=["-c", "--custom-name"]
    )


optnameoptgroup = ArgGroup(
    members=[
        ArgSpec(
            "strfield",
            "A simple string field",
            ["-c", "--custom-name"],
            ArgOpts(required=True, type=str),
        )
    ]
)


@dataclasses.dataclass
class HasSubGroupCase(ConfigClass):
    """Case with a subgroup."""

    subgroup: SimpleOptCase = dataclasses.field()


hassubgroup = ArgGroup(
    subgroups=[ArgSubGroup("subgroup", SimpleOptCase, simpleoptgroup)],
)


@dataclasses.dataclass
class MutuallyExclusiveGroup(ConfigClass):
    """Example mutually exclusive group."""

    opt_a: int = simple("Option A", default=0)
    opt_b: int = simple("Option B", default=0)


@dataclasses.dataclass
class HasMutuallyExclusiveGroupCase(ConfigClass):
    """Case with a mutually exclusive subgroup."""

    subgroup: MutuallyExclusiveGroup = mutually_exclusive_group()


hasmutuallyexclusivegroup = ArgGroup(
    subgroups=[
        ArgSubGroup(
            "subgroup",
            MutuallyExclusiveGroup,
            ArgGroup(
                is_mutually_exclusive=True,
                members=[
                    ArgSpec(
                        "opt-a",
                        "Option A",
                        ["--opt-a"],
                        ArgOpts(type=int, default=0),
                    ),
                    ArgSpec(
                        "opt-b",
                        "Option B",
                        ["--opt-b"],
                        ArgOpts(type=int, default=0),
                    ),
                ],
            ),
        )
    ]
)

# =============================================================================
# Test cases
# =============================================================================

test_group_from_class_cases = {
    "SimpleOptCase": (SimpleOptCase, simpleoptgroup),
    "OptionalOptCase": (OptionalOptCase, optionaloptgroup),
    "PositionalOptCase": (PositionalOptCase, posoptgroup),
    "PositionalAndOptionalCase": (PositionalAndOptionalCase, posplusoptgroup),
    "ChoicesOptCase": (ChoicesOptCase, choicesoptgroup),
    "StoreTrueOptCase": (StoreTrueOptCase, storetrueoptgroup),
    "OptNameOptCase": (OptNameOptCase, optnameoptgroup),
    "HasSubGroupCase": (HasSubGroupCase, hassubgroup),
    "HasMutuallyExclusiveGroupCase": (
        HasMutuallyExclusiveGroupCase,
        hasmutuallyexclusivegroup,
    ),
}


@pytest.mark.parametrize(
    ["configcls", "expectedgroup"],
    test_group_from_class_cases.values(),
    ids=test_group_from_class_cases.keys(),
)
def test_group_from_class(
    configcls: Type[ConfigClass], expectedgroup: ArgGroup
) -> None:
    """
    Test the ArgGroup.from_class function and internally the equivalent for
    ArgSpec and ArgOpts.
    """
    assert ArgGroup.from_class(configcls) == expectedgroup


test_opt_to_kwargs_cases = {
    "empty": (ArgOpts(), {}),
    "simple": (
        ArgOpts(required=True, type=str),
        {"required": True, "type": str},
    ),
    "choices": (
        ArgOpts(choices=["a", "b", "c"]),
        {"choices": ["a", "b", "c"]},
    ),
}


@pytest.mark.parametrize(
    ["opt", "expectedkwargs"],
    test_opt_to_kwargs_cases.values(),
    ids=test_opt_to_kwargs_cases.keys(),
)
def test_opt_to_kwargs(opt: ArgOpts, expectedkwargs: dict[str, Any]) -> None:
    """Test the ArgOpts.to_kwargs() method."""
    assert opt.to_kwargs() == expectedkwargs


test_e2e_parser_cases = {
    "simple": (
        simpleoptgroup,
        ["--strfield", "test"],
        {"strfield": "test"},
    ),
    # =========================================================================
    # Optional argument tests
    "optional_specified": (
        optionaloptgroup,
        ["--optfield", "test"],
        {"optfield": "test"},
    ),
    "optional_not_specified": (
        optionaloptgroup,
        [],
        {"optfield": None},
    ),
    # =========================================================================
    # Positional tests
    "positional": (
        posoptgroup,
        ["a", "B1", "B2"],
        {"posfield": "a", "poslistfield": ["B1", "B2"]},
    ),
    "positional_plus_minimal": (
        posplusoptgroup,
        ["a", "--strfield", "test", "--intfield", "100"],
        {
            "posfield": "a",
            "strfield": "test",
            "intfield": 100,
            "optfield": None,
            "poslistfield": [],
        },
    ),
    "positional_plus_complete": (
        posplusoptgroup,
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
        {
            "strfield": "test",
            "intfield": 100,
            "optfield": "test",
            "posfield": "a",
            "poslistfield": ["X", "Y", "Z"],
        },
    ),
    # =========================================================================
    # Choices tests
    "choices": (
        choicesoptgroup,
        ["--choicefield", "a"],
        {"choicefield": "a"},
    ),
    # =========================================================================
    # Boolean tests
    "store_true_specified": (
        storetrueoptgroup,
        ["--boolfield"],
        {"boolfield": True},
    ),
    "store_true_not_specified": (
        storetrueoptgroup,
        [],
        {"boolfield": False},
    ),
    # =========================================================================
    # Custom option name tests
    "custom_optname": (
        optnameoptgroup,
        ["--custom-name", "test"],
        {"strfield": "test"},
    ),
    "custom_optname_short": (
        optnameoptgroup,
        ["-c", "test"],
        {"strfield": "test"},
    ),
    # =========================================================================
    # Subgroup tests
    "has_subgroup": (
        hassubgroup,
        ["--strfield", "test"],
        {"subgroup": SimpleOptCase(strfield="test")},
    ),
    # =========================================================================
    # Mutually exclusive group tests
    "has_mutually_exclusive_group_NULL": (
        hasmutuallyexclusivegroup,
        [],
        {"subgroup": MutuallyExclusiveGroup(opt_a=0, opt_b=0)},
    ),
    "has_mutually_exclusive_group_A": (
        hasmutuallyexclusivegroup,
        ["--opt-a", "1"],
        {"subgroup": MutuallyExclusiveGroup(opt_a=1, opt_b=0)},
    ),
    "has_mutually_exclusive_group_B": (
        hasmutuallyexclusivegroup,
        ["--opt-b", "1"],
        {"subgroup": MutuallyExclusiveGroup(opt_a=0, opt_b=1)},
    ),
}


@pytest.mark.parametrize(
    ["group", "args", "expectedkwargs"],
    test_e2e_parser_cases.values(),
    ids=test_e2e_parser_cases.keys(),
)
def test_e2e_parser(
    group: ArgGroup, args: Sequence[str], expectedkwargs: dict[str, Any]
) -> None:
    """
    Test the ArgGroup.add_to_parser() and
    ArgGroup.extract_args_from_namespace() methods together.
    """
    parser = argparse.ArgumentParser()
    group.add_to_parser(parser)
    namespace = parser.parse_args(args)
    assert group.extract_args_from_namespace(namespace) == expectedkwargs
