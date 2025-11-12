# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains tools for working with relational data models, written in Python. The primary interface will be Jupyter notebooks using ipywidgets, which import Python modules containing the core tool logic.

## Implementation Status

The **SQL DDL to YAML Translator** is fully implemented:
- ✅ SQL parser using sqlparse library (src/reltools/parsers/sql_parser.py)
- ✅ AST builder converting parsed SQL to Schema objects (src/reltools/parsers/ast_builder.py)
- ✅ YAML converter with proper formatting (src/reltools/converters/yaml_converter.py)
- ✅ Schema validator with comprehensive checks (src/reltools/utils/validators.py)
- ✅ Data models for Schema, Table, Column, ForeignKey (src/reltools/models/schema.py)
- ✅ Comprehensive test suite with integration tests
- ✅ Demo script (demo.py)

## Common Commands

### Installation
```bash
pip install -e ".[dev,notebook]"
```

### Run Demo
```bash
python3 demo.py
```

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_sql_parser.py -v

# With coverage
pytest tests/ --cov=src/reltools --cov-report=html
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/
```

### YAML Output Format

The target YAML structure uses:
- `tables` as the top-level key containing a list of table definitions
- Each table has: `name`, `columns`, `primary_key` (list for multi-column support)
- Each column has: `name`, `type`, optional `constraints`
- Foreign keys defined with: `name`, `columns` (list), `ref_table`, `ref_columns` (list)

Example structure:
```yaml
tables:
  - name: users
    columns:
      - name: id
        type: INTEGER
      - name: username
        type: VARCHAR(50)
        constraints: "NOT NULL"
    primary_key: [id]

  - name: orders
    columns:
      - name: id
        type: INTEGER
      - name: user_id
        type: INTEGER
        constraints: "NOT NULL"
    primary_key: [id]
    foreign_keys:
      - name: fk_orders_user
        columns: [user_id]
        ref_table: users
        ref_columns: [id]
```

## Architecture

### Module Organization

**src/reltools/parsers/**
- `sql_parser.py`: Parses SQL DDL statements using sqlparse, handles CREATE TABLE statements, extracts columns, constraints, primary keys, and foreign keys
- `ast_builder.py`: Converts parsed SQL dictionaries into Schema objects

**src/reltools/converters/**
- `yaml_converter.py`: Converts Schema objects to YAML format with proper structure

**src/reltools/models/**
- `schema.py`: Dataclasses for Schema, Table, Column, ForeignKey

**src/reltools/utils/**
- `validators.py`: Schema validation with comprehensive error checking for foreign key references, duplicate columns, etc.

### Data Flow

```
SQL File → parse_sql_file() → dict
       ↓
ASTBuilder.build() → Schema object
       ↓
ast_to_yaml() → YAML string
       ↓
save_yaml() → YAML file
```

### Key Features

- Supports inline and separate PRIMARY KEY constraints
- Handles multi-column primary and foreign keys
- Validates foreign key references across tables
- Preserves constraint information (NOT NULL, etc.)
- Clean separation between parsing, AST building, and conversion

## Development Environment

- Python 3.8+ required
- Dependencies: pyyaml, sqlparse
- Dev dependencies: pytest, pytest-cov, black, ruff
- Notebook dependencies: jupyter, ipywidgets, notebook
