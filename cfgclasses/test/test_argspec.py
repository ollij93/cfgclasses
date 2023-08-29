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
from cfgclasses.argspec import ArgOpts, Specification, SpecificationItem


# =============================================================================
# Fixtures used in unit tests
# =============================================================================
@dataclasses.dataclass
class SimpleOptCase(ConfigClass):
    """Case with a simple required option."""

    strfield: str = simple("A simple string field")


simpleoptspec = Specification(
    SimpleOptCase,
    members=[
        SpecificationItem(
            "strfield",
            [],
            ArgOpts(
                help="A simple string field",
                metatype=str,
                type=str,
            ),
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
        SpecificationItem(
            "optfield",
            [],
            ArgOpts(
                help="An optional string field",
                metatype=Optional[str],
                type=str,
                default=None,
            ),
        )
    ],
)


@dataclasses.dataclass
class PositionalOptCase(ConfigClass):
    """Case with a positional option."""

    posfield: str = positional("A positional string field")
    poslistfield: list[str] = positional("A positional list field")


posoptspec = Specification(
    PositionalOptCase,
    members=[
        SpecificationItem(
            "posfield",
            None,
            ArgOpts(
                help="A positional string field",
                metatype=str,
                type=str,
            ),
        ),
        SpecificationItem(
            "poslistfield",
            None,
            ArgOpts(
                help="A positional list field",
                metatype=list[str],
                type=str,
                nargs="+",
            ),
        ),
    ],
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


posplusoptspec = Specification(
    PositionalAndOptionalCase,
    members=[
        SpecificationItem(
            "strfield",
            [],
            ArgOpts(
                help="A simple string field",
                metatype=str,
                type=str,
            ),
        ),
        SpecificationItem(
            "posfield",
            None,
            ArgOpts(
                help="A positional string field",
                metatype=str,
                type=str,
            ),
        ),
        SpecificationItem(
            "intfield",
            [],
            ArgOpts(
                help="An integer field",
                metatype=int,
                type=int,
            ),
        ),
        SpecificationItem(
            "optfield",
            [],
            ArgOpts(
                help="An optional string field",
                metatype=Optional[str],
                type=str,
                default=None,
            ),
        ),
        SpecificationItem(
            "poslistfield",
            None,
            ArgOpts(
                help="An optional positional list string field",
                metatype=list[str],
                type=str,
                nargs="*",
                default=[],
            ),
        ),
    ],
)


@dataclasses.dataclass
class ChoicesOptCase(ConfigClass):
    """Case with a choices option."""

    choicefield: str = choices("A choice field", ["a", "b", "c"], default="a")


choicesoptspec = Specification(
    ChoicesOptCase,
    members=[
        SpecificationItem(
            "choicefield",
            [],
            ArgOpts(
                help="A choice field",
                metatype=str,
                type=str,
                choices=["a", "b", "c"],
                default="a",
            ),
        )
    ],
)


@dataclasses.dataclass
class StoreTrueOptCase(ConfigClass):
    """Case with a store_true option."""

    boolfield: bool = store_true("A boolean field")


storetrueoptspec = Specification(
    StoreTrueOptCase,
    members=[
        SpecificationItem(
            "boolfield",
            [],
            ArgOpts(
                help="A boolean field",
                metatype=bool,
                type=bool,
                action="store_true",
                default=False,
            ),
        )
    ],
)


@dataclasses.dataclass
class OptNameOptCase(ConfigClass):
    """Case with a custom option name."""

    strfield: str = simple(
        "A simple string field", optnames=["-c", "--custom-name"]
    )


optnameoptspec = Specification(
    OptNameOptCase,
    members=[
        SpecificationItem(
            "strfield",
            ["-c", "--custom-name"],
            ArgOpts(help="A simple string field", metatype=str, type=str),
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
class MutuallyExclusiveGroup(ConfigClass):
    """Example mutually exclusive group."""

    opt_a: int = simple("Option A", default=0)
    opt_b: int = simple("Option B", default=0)


@dataclasses.dataclass
class HasMutuallyExclusiveGroupCase(ConfigClass):
    """Case with a mutually exclusive subspec."""

    subspec: MutuallyExclusiveGroup = mutually_exclusive_group()


hasmutuallyexclusivegroup = Specification(
    HasMutuallyExclusiveGroupCase,
    subspecs={
        "subspec": Specification(
            MutuallyExclusiveGroup,
            is_mutually_exclusive=True,
            members=[
                SpecificationItem(
                    "opt-a",
                    [],
                    ArgOpts(
                        help="Option A", metatype=int, type=int, default=0
                    ),
                ),
                SpecificationItem(
                    "opt-b",
                    [],
                    ArgOpts(
                        help="Option B", metatype=int, type=int, default=0
                    ),
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
    "PositionalOptCase": (PositionalOptCase, posoptspec),
    "PositionalAndOptionalCase": (PositionalAndOptionalCase, posplusoptspec),
    "ChoicesOptCase": (ChoicesOptCase, choicesoptspec),
    "StoreTrueOptCase": (StoreTrueOptCase, storetrueoptspec),
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
    SpecificationItem and ArgOpts.
    """
    assert Specification.from_class(configcls) == expectedspec


test_opt_to_kwargs_cases = {
    "required": (
        ArgOpts(help="is required", metatype=str, type=str),
        False,
        {"help": "is required", "required": True, "type": str},
    ),
    "optional": (
        ArgOpts(help="is optional", metatype=Optional[str], type=str),
        False,
        {"help": "is optional", "type": str},
    ),
    "positional": (
        ArgOpts(help="is positional", metatype=str, type=str),
        True,
        {"help": "is positional", "type": str},
    ),
    "choices": (
        ArgOpts(
            help="has choices", metatype=str, type=str, choices=["a", "b", "c"]
        ),
        False,
        {
            "help": "has choices",
            "required": True,
            "choices": ["a", "b", "c"],
            "type": str,
        },
    ),
}


@pytest.mark.parametrize(
    ["opt", "positional_", "expectedkwargs"],
    test_opt_to_kwargs_cases.values(),
    ids=test_opt_to_kwargs_cases.keys(),
)
def test_opt_to_kwargs(
    opt: ArgOpts, positional_: bool, expectedkwargs: dict[str, Any]
) -> None:
    """Test the ArgOpts.to_kwargs() method."""
    assert opt.to_kwargs(positional_) == expectedkwargs


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
        ["a", "--strfield", "test", "--intfield", "100"],
        PositionalAndOptionalCase(
            posfield="a",
            strfield="test",
            intfield=100,
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
        StoreTrueOptCase(boolfield=True),
    ),
    "store_true_not_specified": (
        storetrueoptspec,
        [],
        StoreTrueOptCase(boolfield=False),
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
