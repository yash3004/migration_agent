from langgraph.graph import StateGraph, START, END
from dataclasses import dataclass
from migration_agent import load_config
from migration_agent.agents import (
    SchemaAnalystAgent,
    ValidationAgent,
    SQLGeneratorAgent,
    ExplainerAgent,
)
from pathlib import Path
import logging
import os

_logger = logging.getLogger("orchestrator")


@dataclass
class State:
    contexts: list = None
    sql_script: str = ""
    validation_report: dict = None
    explanation: str = ""
    retry_count: int = 0


def sql_generator_node(state: State):
    _logger.info("sql generator agent is generating sql for all tables")
    sql_agent = SQLGeneratorAgent()
    sql_script = sql_agent.generate(state.contexts)
    _logger.info("✓ SQL generated\n")
    return {"sql_script": sql_script}


def validator_node(state: State):
    _logger.info("validation agent is validating sql")
    validator_agent = ValidationAgent()
    report = validator_agent.validate(state.sql_script, state.contexts[0])
    _logger.info(f"{len(report.warnings)} warnings, {len(report.errors)} errors\n")
    return {"validation_report": report}


def explainer_node(state: State):
    _logger.info("explainer agent")
    explanation_agent = ExplainerAgent()
    explanation = explanation_agent.explain(state.sql_script, state.contexts[0])
    _logger.info("✓ Explanation generated\n")
    return {"explanation": explanation}


def sql_regenerator_node(state: State):
    _logger.info(f"🔄 Retry {state.retry_count + 1}/3")
    generate_agent = SQLGeneratorAgent()
    sql = generate_agent.regenerate(state.contexts, state.validation_report)
    return {"sql_script": sql, "retry_count": state.retry_count + 1}


def check_validation(state: State):
    if not state.validation_report.has_errors:
        return "Pass"
    return "Retry" if state.retry_count < 3 else "Fail"


def start():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    os.environ["OPENAI_API_KEY"] = load_config().openai.api_key

    _logger.info("🚀 AI Data Migration Orchestrator\n")

    workflow = StateGraph(State)
    workflow.add_node("sql_generator", sql_generator_node)
    workflow.add_node("sql_regenerator", sql_regenerator_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("explainer", explainer_node)

    workflow.add_edge(START, "sql_generator")
    workflow.add_edge("sql_generator", "validator")
    workflow.add_conditional_edges(
        "validator",
        check_validation,
        {"Pass": "explainer", "Retry": "sql_regenerator", "Fail": END},
    )
    workflow.add_edge("sql_regenerator", "validator")
    workflow.add_edge("explainer", END)

    chain = workflow.compile()

    _logger.info("schema analyst analysing schemas..")
    contexts = SchemaAnalystAgent().analyze(
        "data/source_schema.json", "data/target_schema.json", "data/field_mapping.csv"
    )
    _logger.info(f"found {len(contexts)} tables\n")

    result = chain.invoke({"contexts": contexts})

    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)

    with open(outputs_dir / "sample_output.sql", "w") as f:
        f.write(result["sql_script"])

    with open(outputs_dir / "validation_report.md", "w") as f:
        f.write("# Validation Report\n\n")
        report = result["validation_report"]
        for vm in report.valid_mappings:
            f.write(f"{vm}\n")
        f.write("\n### Warnings\n")
        for w in report.warnings:
            f.write(f"{w}\n")
        if report.errors:
            f.write("\n### Errors\n")
            for e in report.errors:
                f.write(f"{e}\n")

    with open(outputs_dir / "sql_explanation.md", "w") as f:
        f.write("# SQL Explanation\n\n")
        f.write(result["explanation"])

    _logger.info("\nmigration script generated")
    _logger.info(f"Outputs: {outputs_dir.absolute()}")
