import json
import pathlib
from typing import Any
import warnings

import yaml
from typing_extensions import Literal

from mztab_m_io.model.mztabm import MzTabM
from mztab_m_io.model.serialization import SerializationContext


def read(file_path: str, format: Literal["tsv", "json", "yaml"] = "tsv") -> MzTabM:
    """Read and parse an mzTab-M file in TSV, JSON, or YAML format.

    This function reads an mzTab-M formatted file and attempts to parse it into an MzTabM object.
    The parsing includes validation of the content against the mzTab-M specification.

    Args:
        file_path: Path to the mzTab-M file to read.
        format: The format of the input file. One of:
            - "tsv": Tab-separated values (default)
            - "json": JSON format
            - "yaml": YAML format

    Returns:
        The parsed MzTabM object

    Raises:
        ValidationError: If specified file violates the data model
        ValueError: If file_path is empty or format is invalid
        FileNotFoundError: If the specified file does not exist

    Example:
        >>> import warnings
        >>> with warnings.catch_warnings(record=True) as w:
        ...     try:
        ...         mztabm = read("example.mztab", format="tsv")
        ...     except Exception as error:
        ...         print("Failed to load file")
        ...         raise error
        ...     else:
        ...         print(f"Loaded mzTab-M file")
        ...     finally:
        ...         print(f"Encountered {len(w)} warnings")
    """
    if not file_path:
        raise ValueError("Invalid file path")
    if not format:
        raise ValueError("Invalid file format.")

    input_path = pathlib.Path(file_path)
    if not input_path.exists():
        raise ValueError("Input file does not exist.")

    if format == "tsv":
        content = input_path.read_text()
    elif format == "json":
        with input_path.open() as f:
            content = json.load(f)
    elif format == "yaml":
        with input_path.open() as f:
            content = yaml.safe_load(f)
        format = "json"
    else:
        raise ValueError(f"invalid format type: {format}")

    return MzTabM.model_validate(
        content, by_alias=True, context=dict(source_format=format)
    )


def write(
    mztabm: MzTabM, file_path: str, format: Literal["tsv", "json", "yaml"] = "tsv"
) -> bool:
    """Write an MzTabM object to a file in TSV, JSON, or YAML format.

    This function serializes an MzTabM object to the specified format and writes it to a file.
    The target directory will be created if it doesn't exist.

    Args:
        mztabm: The MzTabM object to serialize
        file_path: Path where the file should be written
        format: The desired output format. One of:
            - "tsv": Tab-separated values (default)
            - "json": JSON format
            - "yaml": YAML format

    Returns:
        bool: True if the file was successfully written

    Raises:
        ValueError: If mztabm is None, file_path is empty, or format is invalid

    Example:
        >>> mztabm = read("example.mztab")
        >>> success = write(mztabm, "output.mztab")
        >>> if success:
        ...     print("File written successfully")
        ... else:
        ...     print("Failed to write file")
    """
    if not mztabm:
        raise ValueError("Invalid mzTab-M input")
    if not file_path:
        raise ValueError("Invalid file path")
    if not format:
        raise ValueError("Invalid file format.")

    if format == "tsv":
        result = str(mztabm)
    elif format in {"json", "yaml"}:
        result = mztabm.model_dump_json(
            by_alias=True,
            indent=2,
            exclude_none=True,
        )
        if format == "yaml":
            json_obj = json.loads(result)
            result = yaml.safe_dump(json_obj, sort_keys=False)

    target_path = pathlib.Path(file_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(file_path).write_text(result)
    return True


def load_from_dict(data: dict[str, Any]) -> MzTabM:
    """Load and validate an MzTabM object from a dictionary.

    This function takes a dictionary representation of an mzTab-M file and attempts to
    validate and convert it into an MzTabM object. The dictionary should follow the
    mzTab-M structure with proper field names and data types.

    Args:
        data: A dictionary containing mzTab-M data. The structure should match
             the mzTab-M specification with proper field names and nested objects.

    Returns:
        The parsed MzTabM object

    Example:
        >>> result = load_from_dict(data)
        >>> if result.success:
        ...     mztabm = result.mztabm
        ...     print("Data loaded successfully")
        ... else:
        ...     print("Validation failed:")
        ...     for msg in result.messages:
        ...         print(f"{msg.message_type}: {msg.message}")
    """
    warnings.warn(
        message="Directly validate the MzTabM object", category=DeprecationWarning
    )
    return MzTabM.model_validate(
        data, by_alias=True, context=dict(source_format="json")
    )


def convert_to_dict(mztabm: MzTabM) -> dict[str, Any]:
    """Convert an MzTabM object to a dictionary representation.

    This function converts an MzTabM object into a dictionary format suitable for
    serialization to JSON or other formats. The conversion uses field aliases and
    excludes None values to create a clean representation.

    Args:
        mztabm: The MzTabM object to convert

    Returns:
        dict[str, Any]: Dictionary representation of the MzTabM object

    Raises:
        ValueError: If mztabm is None

    Example:
        >>> mztabm = read("example.mztab")
        >>> dict_data = convert_to_dict(mztabm)
        >>> print(f"Converted object with {len(dict_data)} top-level keys")
    """
    if not mztabm:
        raise ValueError("Invalid mzTab-M input")

    return mztabm.model_dump(
        context=SerializationContext(convert_to="json"),
        by_alias=True,
        exclude_none=True,
    )
