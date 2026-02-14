from pydantic import BaseModel
from typing import List, Optional, Dict

class SchemaField(BaseModel):
    name: str
    type: str
    nullable: bool
    primary_key: Optional[bool] = False

class Schema(BaseModel):
    table_name: str
    fields: List[SchemaField]

class MultiTableSchema(BaseModel):
    tables: List[Schema]

class FieldMapping(BaseModel):
    source_field: str
    target_field: str
    transformation: str
    source_table: Optional[str] = None
    target_table: Optional[str] = None

class MigrationContext(BaseModel):
    source_schema: Schema
    target_schema: Schema
    mappings: List[FieldMapping]
    analysis: Optional[str] = None
    validated_mappings: List[dict] = []
    missing_in_target: List[str] = []
    datatype_mismatches: List[dict] = []

class ValidationReport(BaseModel):
    has_errors: bool
    warnings: List[str] = []
    errors: List[str] = []
    valid_mappings: List[str] = []
    validation_details: str = None
