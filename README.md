# Tools for Relational Data Modelling

This repository contains a set of tools for working with relational data models, written in Python.

- All tools are programmed in Python
- User interfaces provided by Jupyter notebooks using ipywidgets
- Modular architecture with separate parsers, converters, and validators
- Comprehensive test suite

## Installation

Install the package with all dependencies:

```bash
pip install -e ".[dev,notebook]"
```

Or install core dependencies only:

```bash
pip install pyyaml sqlparse
```

## Quick Start

Try the demo script to see the SQL to YAML converter in action:

```bash
python3 demo.py
```

## SQL DDL to YAML Translator

**Status: ✅ Implemented**
The SQL DDL to YAML translator converts SQL CREATE TABLE statements into structured YAML format.

### Features

- ✅ Parse SQL DDL files and strings
- ✅ Support for single and multi-column primary keys
- ✅ Support for foreign key constraints
- ✅ Column data types and constraints
- ✅ Schema validation
- ✅ Comprehensive test coverage

### Usage

```python
from src.reltools.parsers.sql_parser import parse_sql_file
from src.reltools.parsers.ast_builder import ASTBuilder
from src.reltools.converters.yaml_converter import ast_to_yaml, save_yaml

# Parse SQL file
parsed_sql = parse_sql_file('schema.sql')

# Build AST
builder = ASTBuilder()
schema = builder.build(parsed_sql)

# Convert to YAML
yaml_output = ast_to_yaml(schema)

# Save to file
save_yaml(yaml_output, 'output.yaml')
```

### Output Format

The YAML file has the following structure:
  ```yaml
  tables:
  - name: users
    columns:
      - name: id
        type: INTEGER
      - name: username
        type: VARCHAR(50)
        constraints: "NOT NULL"
      - name: email
        type: VARCHAR(100)
        constraints: "NOT NULL"
    primary_key: [id]   # list to also support multi-column primary key
  
  - name: orders
    columns:
      - name: id
        type: INTEGER
      - name: user_id
        type: INTEGER
        constraints: "NOT NULL"
      - name: user_email
        type: VARCHAR(100)
        constraints: "NOT NULL"
      - name: order_date
        type: DATETIME
        constraints: "NOT NULL"
      - name: total
        type: DECIMAL(10,2)
    primary_key: [id]
    foreign_keys:
      - name: fk_orders_user
        columns: [user_id] # list to also support multi-column foreign key
        ref_table: users
        ref_columns: [id]
  ```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development instructions, including:
- Running tests
- Code formatting and linting
- Creating Jupyter notebooks
- Adding new features

## Project Structure

```
reltools/
├── src/reltools/         # Core library
│   ├── parsers/          # SQL parsing and AST building
│   ├── converters/       # Format converters
│   ├── models/           # Data models
│   └── utils/            # Utilities and validators
├── notebooks/            # Jupyter notebooks
├── tests/                # Test suite
│   └── fixtures/         # Test data
├── data/                 # Input/output data
└── docs/                 # Documentation
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/reltools --cov-report=html
```

## License

TBD