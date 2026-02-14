from migration_agent.models import MigrationContext, ValidationReport
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from migration_agent import load_config
import json

_config = load_config()

class ValidationAgent:
    """Verifies data type compatibility and identifies errors or missing mappings using LLM"""
    
    def __init__(self):
        self.api_key = _config.openai.api_key
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=self.api_key).with_structured_output(ValidationReport)
    
    def validate(self, sql_script: str, context: MigrationContext) -> ValidationReport:
        """Validate SQL against schema constraints using LLM"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Validate SQL migration scripts. Return valid_mappings as strings like 'source→target'."),
            ("user", """SQL:
{sql_script}

Source: {source_table} ({source_fields})
Target: {target_table} ({target_fields})
Mappings: {mappings}

Validate datatype compatibility, missing mappings, and SQL structure.""")
        ])
        
        source_fields = ", ".join([f"{f.name}:{f.type}" for f in context.source_schema.fields])
        target_fields = ", ".join([f"{f.name}:{f.type}" for f in context.target_schema.fields])
        mappings = ", ".join([f"{m['source']}→{m['target']}" for m in context.validated_mappings])
        
        return self.llm.invoke(prompt.format_messages(
            sql_script=sql_script,
            source_table=context.source_schema.table_name,
            target_table=context.target_schema.table_name,
            source_fields=source_fields,
            target_fields=target_fields,
            mappings=mappings
        ))
