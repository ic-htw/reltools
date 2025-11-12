# Development Guide

## Setup

### 1. Install Dependencies

First, install the package with development dependencies:

```bash
pip install -e ".[dev,notebook]"
```

Or install dependencies separately:

```bash
pip install pyyaml sqlparse pytest pytest-cov jupyter ipywidgets notebook black ruff
```

### 2. Run the Demo

Try out the SQL to YAML converter with the demo script:

```bash
python3 demo.py
```

This will:
- Parse the sample SQL DDL file (`tests/fixtures/sample_ddl.sql`)
- Build an Abstract Syntax Tree
- Convert to YAML format
- Validate the schema
- Save the output to `data/output/demo_output.yaml`

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Files

```bash
pytest tests/test_sql_parser.py -v
pytest tests/test_yaml_converter.py -v
pytest tests/test_validators.py -v
pytest tests/test_integration.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src/reltools --cov-report=html
```

View the coverage report by opening `htmlcov/index.html` in your browser.

## Code Quality

### Format Code with Black

```bash
black src/ tests/
```

### Lint with Ruff

```bash
ruff check src/ tests/
```

## Project Structure

```
src/reltools/
├── parsers/          # SQL parsing and AST building
├── converters/       # Format converters (YAML, etc.)
├── models/           # Data models (Schema, Table, Column)
└── utils/            # Utilities (validators, etc.)

tests/
├── fixtures/         # Test data files
├── test_sql_parser.py
├── test_yaml_converter.py
├── test_validators.py
└── test_integration.py

notebooks/            # Jupyter notebooks for UI
```

## Usage Examples

### Parse SQL and Convert to YAML

```python
from src.reltools.parsers.sql_parser import parse_sql_file
from src.reltools.parsers.ast_builder import ASTBuilder
from src.reltools.converters.yaml_converter import ast_to_yaml

# Parse SQL file
parsed = parse_sql_file('path/to/schema.sql')

# Build AST
builder = ASTBuilder()
schema = builder.build(parsed)

# Convert to YAML
yaml_output = ast_to_yaml(schema)
print(yaml_output)
```

### Validate Schema

```python
from src.reltools.utils.validators import validate_schema
import yaml

# Load YAML file
with open('schema.yaml', 'r') as f:
    schema = yaml.safe_load(f)

# Validate
try:
    validate_schema(schema)
    print("Schema is valid!")
except SchemaValidationError as e:
    print(f"Validation error: {e}")
```

## Creating Notebooks

Jupyter notebooks should be placed in the `notebooks/` directory and can import the reltools modules:

```python
from src.reltools.parsers.sql_parser import parse_sql_string
from src.reltools.converters.yaml_converter import ast_to_yaml
from notebooks.widgets.custom_widgets import create_file_upload_widget

# Your notebook code here
```

## Adding New Features

1. Create the implementation in the appropriate module under `src/reltools/`
2. Add tests in `tests/`
3. Run tests to ensure everything works
4. Update documentation if needed
