from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from migration_agent.models import MigrationContext
from migration_agent import load_config
import logging

_sql_generator_logger = logging.getLogger("SQLGeneratorAgent")

_config = load_config()


class SQLGeneratorAgent:
    """Generates SQL INSERT INTO SELECT statements using LLM"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0, api_key=_config.openai.api_key
        )

    def generate(self, contexts: list) -> str:
        """Generate SQL for all tables at once"""
        all_analyses = "\n\n".join(
            [f"Table {i+1}: {ctx.analysis}" for i, ctx in enumerate(contexts)]
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Generate only SQL INSERT INTO ... SELECT statements. No explanations, no markdown, no notes.",
                ),
                (
                    "user",
                    """Schema Analysis:{analyses}

Generate SQL only:""",
                ),
            ]
        )

        response = self.llm.invoke(prompt.format_messages(analyses=all_analyses))
        _sql_generator_logger.info(response.content.strip())
        
        return response.content.strip()

    def regenerate(self, contexts: list, validation_report) -> str:
        """Regenerate SQL for all tables based on validation errors"""
        all_analyses = "\n\n".join(
            [f"Table {i+1}: {ctx.analysis}" for i, ctx in enumerate(contexts)]
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Generate only corrected SQL INSERT INTO ... SELECT statements. No explanations."),
                (
                    "user",
                    """Errors:
{errors}

Warnings:
{warnings}

Schema Analysis:
{analyses}

Generate SQL only:""",
                ),
            ]
        )

        response = self.llm.invoke(
            prompt.format_messages(
                errors="\n".join(validation_report.errors),
                warnings="\n".join(validation_report.warnings),
                analyses=all_analyses,
            )
        )

        return response.content.strip()
