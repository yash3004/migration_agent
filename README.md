# AI Data Migration Orchestrator

Multi-agent system for generating SQL migration scripts using LLMs.

## Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure API Key

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run

```bash
python -m migration_agent.main
```

## Input Files

Place these in `data/` directory:

- `source_schema.json` - Source database schema
- `target_schema.json` - Target database schema
- `field_mapping.csv` - Field mappings

### Example: source_schema.json

```json
{
  "table_name": "raisers_edge_donors",
  "fields": [
    {"name": "donor_fname", "type": "VARCHAR(100)", "nullable": false},
    {"name": "donor_lname", "type": "VARCHAR(100)", "nullable": false}
  ]
}
```

### Example: field_mapping.csv

```csv
source_field,target_field,transformation
donor_fname,first_name,direct
donor_lname,last_name,direct
```

## Output Files

Generated in `outputs/` directory:

- `sample_output.sql` - SQL migration script
- `validation_report.md` - Validation results
- `sql_explanation.md` - Human-readable explanation

## Architecture

4 agents in linear pipeline:

```
Schema Analyst → SQL Generator → Validator → Explainer
```

1. **Schema Analyst** - Analyzes schemas, detects mismatches
2. **SQL Generator** - Generates SQL using LLM
3. **Validator** - Validates SQL against constraints
4. **Explainer** - Generates human-readable explanation

## Requirements

- Python 3.11+
- OpenAI API key
- Dependencies: LangChain, LangGraph, OpenAI

## Project Structure

```
ai-agentic-migration/
├── src/migration_agent/
│   ├── agents/          # 4 agent implementations
│   ├── main.py          # Workflow orchestration
│   └── models.py        # Pydantic models
├── data/                # Input schemas and mappings
├── outputs/             # Generated SQL and reports
└── config.yaml          # Configuration
```

## Configuration

Edit `config.yaml`:

```yaml
openai:
  api_key: ${OPENAI_API_KEY}
```

## Troubleshooting

**Error: "OPENAI_API_KEY not found"**
- Create `.env` file with `OPENAI_API_KEY=your-key`

**Error: "No module named migration_agent"**
- Run from project root: `python -m migration_agent.main`

**Validation fails**
- Check field mappings in CSV
- Verify schema field names match exactly
