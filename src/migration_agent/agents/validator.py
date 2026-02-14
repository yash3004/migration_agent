from migration_agent.models import MigrationContext, ValidationReport
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from migration_agent import load_config
import logging

_config = load_config()
_validation_logger = logging.getLogger("ValidationAgent")
class ValidationAgent:
    """Verifies data type compatibility and identifies errors or missing mappings using LLM"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0, 
            api_key=_config.openai.api_key
        ).with_structured_output(ValidationReport)
    
    def validate(self, sql_script: str, context: MigrationContext) -> ValidationReport:
        """Validate SQL against schema constraints using LLM"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You're a SQL validation expert. Validate the SQL migration script."),
            ("user", """SQL Script:
{sql_script}

Source Table: {source_table}
Source Fields: {source_fields}

Target Table: {target_table}
Target Fields: {target_fields}

Field Mappings: {mappings}

Validate and return structured report.""")
        ])
        
        source_fields = ", ".join([f"{f.name}:{f.type}" for f in context.source_schema.fields])
        target_fields = ", ".join([f"{f.name}:{f.type}" for f in context.target_schema.fields])
        mappings = ", ".join([f"{m['source']}→{m['target']}" for m in context.validated_mappings])
        
        report = self.llm.invoke(prompt.format_messages(
            sql_script=sql_script,
            source_table=context.source_schema.table_name,
            target_table=context.target_schema.table_name,
            source_fields=source_fields,
            target_fields=target_fields,
            mappings=mappings
        ))
        
        _validation_logger.info(report.model_dump_json(indent=2))
        return report
