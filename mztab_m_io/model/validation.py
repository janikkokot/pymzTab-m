import enum
from typing import List, Literal, Optional

from mztab_m_io.model import MzTabBaseModel


class Error(MzTabBaseModel):
    code: int
    message: str


class Category(enum.Enum):
    FORMAT = "format"
    LOGICAL = "logical"
    CROSS_CHECK = "cross_check"


class MessageType(enum.Enum):
    ERROR = "error"
    WARNING = "warn"
    INFO = "info"


class ValidationMessage(MzTabBaseModel):
    code: str = ""
    category: Category
    message_type: Optional[MessageType] = "info"
    message: str
    line_number: Optional[int] = None


class ValidationSummary(MzTabBaseModel):
    messages: Optional[List[ValidationMessage]] = None
    source_format: Literal["tsv", "json"] = "tsv"


class CrossCheckWarning(UserWarning):
    def __init__(self, message):
        self.message = message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.message!r}"
