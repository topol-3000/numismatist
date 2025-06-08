from pydantic import BaseModel, ConfigDict


class SchemaConfigMixin(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        validate_return=True,
        validate_default=True,
    )
