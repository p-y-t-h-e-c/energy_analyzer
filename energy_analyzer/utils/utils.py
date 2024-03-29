"""Miscellenious utilities.

Utils:
- assert_never: Can be used to run exhaustive checks on Literals and Enums (see the
    docstring for examples)
"""
from typing import NoReturn


# FIXME: Mypy shows a type error when the check is exhaustive:
#   python_package/common/logger.py:106: error: Argument 1 to "assert_never" has incompatible type "Environment"; expected "NoReturn"  [arg-type]  # noqa: E501
#   If the above error shows up it means the code checks everything, but they share the
#   same error code `[arg-type]` with the check we want to return.
#   Could this be a mypy error?
def assert_never(value: NoReturn) -> NoReturn:
    """Check that every value in an Enum was checked.

    This function, paired with mypy, will let us know if we have tested that an Enum was
    fully checked. This allows us to make sure that we are always handling every case.

    For example:
    ```python
    from enum import Enum


    class Environment(Enum):
        LOCAL = "LOCAL"
        PRODUCTION = "PRODUCTION"


    def get_config(environment: Environment) -> Config:
        match environment:
            case Environment.LOCAL:
                return LocalConfig()
            case _:
                assert_never(environment)
    ```

    > The above never handles production, so running `mypy <path_to_config>` returns:

    ```shell
    python_package/common/config.py:36: error: Argument 1 to "assert_never" has \
incompatible type "Literal[Environment.PRODUCTION]"; expected "NoReturn"
    ```

    > If all are handled then we get this error with mypy:

    ```shell
    ```

    :param value: Place the Enum being checked here, it should be a NoReturn type by the
        time it reaches this function if the Enum was exhaustively tested.

    :returns: Nothing is returned, instead it will raise an assertion error.

    :raises AssertionError: If the Enum was not exhaustively tested.
    """
    assert False, f"Unhandled value: {value} ({type(value).__name__})"
