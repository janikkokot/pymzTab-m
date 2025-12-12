import abc
import warnings
import enum
from typing import (
    Annotated,
    Any,
    Optional,
    Union,
)

from pydantic import (
    AnyUrl,
    Field,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    BaseModel,
    ConfigDict,
)
from pydantic.alias_generators import to_camel, to_pascal

from mztab_m_io.model.serialization import (
    MetadataDictInfo,
    MetadataSerialization,
    SerializationContext,
)


class SerializationCategory(str, enum.Enum):
    STRING = "string"
    INTEGER = "integer"
    OBJECT = "object"
    STRING_LIST = "string_list"
    INTEGER_LIST = "integer_list"
    OBJECT_LIST = "object_list"


class CustomSerializer(abc.ABC):
    def serialize(self) -> str:
        pass


class MzTabBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_default=True,
        validate_assignment=True,
        validation_error_cause=True,
        field_title_generator=lambda field_name, field_info: to_pascal(
            field_name.replace("_", " ").strip()
        ),
    )

    def serialize_to_json(
        self, handler: SerializerFunctionWrapHandler, info: SerializationInfo
    ) -> tuple[bool, dict[str, Any]]:
        warnings.warn(
            "It is prefered to use `model_dump_json` instead.", DeprecationWarning
        )
        if info and isinstance(info.context, SerializationContext):
            if info.context.convert_to and info.context.convert_to.lower() == "json":
                return True, handler(self)
        return False, {}

    def serialize(self, prefix: str) -> list[str]:
        lines: list[str] = []
        for field, field_info in self.__class__.model_fields.items():
            serializer_model = field_info.json_schema_extra or {}
            extra = MetadataSerialization.model_validate(serializer_model)
            if extra.ignore:
                continue
            alias = field_info.alias if field_info.alias else field
            key_name = alias
            if prefix:
                key_name = prefix if extra.object_level_value else f"{prefix}-{alias}"

            try:
                value = getattr(self, field)
            except AttributeError:
                continue
            if isinstance(value, (str, AnyUrl)):
                line = f"{key_name}\t{value or ''}"
                lines.append(line)
            elif isinstance(value, int):
                if extra.referenced_field_name:
                    ref = extra.referenced_field_name
                    line = f"{key_name}\t{ref}[{value}]"
                else:
                    line = f"{key_name}\t{value}"
                lines.append(line)
            elif isinstance(value, MzTabBaseModel):
                lines.extend(value.serialize(prefix=key_name))
            elif isinstance(value, list):
                if not value:
                    continue
                if isinstance(value[0], (str, AnyUrl)):
                    separator = extra.list_concatenation_str
                    if separator:
                        line_value = separator.join([str(x) for x in value])
                        line = f"{key_name}\t{line_value}"
                    else:
                        for idx, item in enumerate(value, start=1):
                            indexed_key_name = f"{key_name}[{idx}]"
                            line = f"{indexed_key_name}\t{item or ''}"
                            lines.append(line)
                elif isinstance(value[0], int):
                    separator = extra.list_concatenation_str or "|"
                    if extra.referenced_field_name:
                        values = [f"{extra.referenced_field_name}[{x}]" for x in value]
                        line_value = separator.join(values)
                        line = f"{key_name}\t{line_value}"
                    else:
                        values = [str(x) for x in value if x is not None]
                        line = f"{key_name}\t{separator.join(values)}"
                    lines.append(line)
                elif isinstance(value[0], MzTabBaseModel):
                    separator = extra.list_concatenation_str or None
                    if separator:
                        line_value = separator.join([str(x) for x in value])
                        line = f"{key_name}\t{line_value or ''}"
                        lines.append(line)
                    else:
                        for idx, item in enumerate(value, start=1):
                            indexed_key_name = f"{key_name}[{idx}]"
                            if extra.non_indexed_list_value:
                                indexed_key_name = key_name
                            elif isinstance(item, IdentifiableModel):
                                id_val = item.get_id()
                                if id_val:
                                    indexed_key_name = f"{key_name}[{id_val}]"
                            lines.extend(item.serialize(prefix=indexed_key_name))
                else:
                    warnings.warn("not expected")

            else:
                warnings.warn(f"Skipping unsupported value {key_name!r} {extra!r}")
        return lines


class SerializableModel(MzTabBaseModel):
    __field_info__: Union[None, MetadataDictInfo] = None

    @classmethod
    def get_dict_info(cls):
        if cls.__field_info__:
            return cls.__field_info__

        dict_info = MetadataDictInfo(field_type=cls)

        for field, field_info in cls.model_fields.items():
            extra = field_info.json_schema_extra or {}
            json_extra = MetadataSerialization.model_validate(extra, by_alias=True)
            if json_extra.ignore:
                continue
            field_name = field_info.validation_alias or field
            if json_extra.object_level_value:
                dict_info.object_level_value_field = field_name
            if json_extra.list_concatenation_str:
                dict_info.list_concatenation_str_dict[field_name] = (
                    json_extra.list_concatenation_str
                )
            if json_extra.referenced_field_name:
                dict_info.referenced_field_names[field_name] = (
                    json_extra.referenced_field_name
                )
            if json_extra.ignore:
                dict_info.ignore_filed_names.add(field_name)
            if json_extra.non_indexed_list_value:
                dict_info.non_indexed_list_values.add(field_name)
        cls.__field_info__ = dict_info
        return dict_info


class IdentifiableModel(SerializableModel):
    id: Annotated[
        Optional[int],
        Field(
            ge=1,
            json_schema_extra=MetadataSerialization(ignore=True).model_dump(
                exclude_unset=True, exclude_defaults=True
            ),
        ),
    ] = None

    def get_id(self):
        return self.id
