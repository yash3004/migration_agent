from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from migration_agent import load_config

_config = load_config()


class ExplainerAgent:
    # gives explaination
    def __init__(self):
        self.api_key = _config.openai.api_key
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=self.api_key)

    def explain(self, sql_script: str, context) -> str:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You're a technical writer. Explain SQL migration scripts in simple terms for audit documentation."),
                ("user", """SQL Script:
{sql_script}

Source Table: {source_table}
Target Table: {target_table}

Provide a clear explanation in markdown format.""")
            ]
        )

        response = self.llm.invoke(
            prompt.format_messages(
                sql_script=sql_script,
                source_table=context.source_schema.table_name,
                target_table=context.target_schema.table_name,
            )
        )

        return response.content.strip()
