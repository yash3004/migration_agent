import json
import csv
from migration_agent.models import (
    Schema,
    FieldMapping,
    MigrationContext,
    MultiTableSchema,
)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from migration_agent import load_config
import logging

_config = load_config()
_schema_analyst_logger = logging.getLogger("SchemaAnalystAgent")


class SchemaAnalystAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0, api_key=_config.openai.api_key
        )

    def analyze(self, source_path: str, target_path: str, mapping_path: str) -> list:
        with open(source_path) as f:
            source_data = MultiTableSchema(**json.load(f))
        with open(target_path) as f:
            target_data = MultiTableSchema(**json.load(f))

        mappings = []
        with open(mapping_path) as f:
            for row in csv.DictReader(f):
                mappings.append(FieldMapping(**row))

        table_pairs = {}
        for m in mappings:
            key = (m.source_table, m.target_table)
            if key not in table_pairs:
                table_pairs[key] = []
            table_pairs[key].append(m)

        contexts = []
        for (src_name, tgt_name), maps in table_pairs.items():
            src_schema = next(
                (t for t in source_data.tables if t.table_name == src_name), None
            )
            tgt_schema = next(
                (t for t in target_data.tables if t.table_name == tgt_name), None
            )

            if not src_schema or not tgt_schema:
                continue

            context = self._analyze_with_llm(src_schema, tgt_schema, maps)
            contexts.append(context)

        return contexts

    def _analyze_with_llm(
        self, src_schema: Schema, tgt_schema: Schema, maps: list
    ) -> MigrationContext:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Analyze database schema compatibility for migration."),
                (
                    "user",
                    """Source: {source_table} ({source_fields})
                Target: {target_table} ({target_fields})
                Mappings: {mappings}

            Analyze datatype compatibility, missing fields, and valid mappings.""",
                ),
            ]
        )

        src_fields = ", ".join([f"{f.name}:{f.type}" for f in src_schema.fields])
        tgt_fields = ", ".join([f"{f.name}:{f.type}" for f in tgt_schema.fields])
        mappings_str = ", ".join([f"{m.source_field}→{m.target_field}" for m in maps])

        response = self.llm.invoke(
            prompt.format_messages(
                source_table=src_schema.table_name,
                target_table=tgt_schema.table_name,
                source_fields=src_fields,
                target_fields=tgt_fields,
                mappings=mappings_str,
            )
        )
        _schema_analyst_logger.info(response.content)

        context = MigrationContext(
            source_schema=src_schema,
            target_schema=tgt_schema,
            mappings=maps,
            analysis=response.content,
        )

        src_field_map = {f.name: f for f in src_schema.fields}
        tgt_field_map = {f.name: f for f in tgt_schema.fields}

        for m in maps:
            src = src_field_map.get(m.source_field)
            tgt = tgt_field_map.get(m.target_field)

            if not tgt:
                context.missing_in_target.append(m.target_field)
            elif src and src.type != tgt.type:
                context.datatype_mismatches.append(
                    {
                        "source": m.source_field,
                        "target": m.target_field,
                        "source_type": src.type,
                        "target_type": tgt.type,
                    }
                )
            else:
                context.validated_mappings.append(
                    {"source": m.source_field, "target": m.target_field}
                )

        return context
