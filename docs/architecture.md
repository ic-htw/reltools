# Architecture

## Overview

Reltools is designed as a modular toolkit for working with relational data models.

## Component Structure

### Parsers
- `sql_parser.py`: Parses SQL DDL statements from files or strings
- `ast_builder.py`: Constructs abstract syntax trees from parsed SQL

### Converters
- `yaml_converter.py`: Converts AST to YAML format

### Models
- `schema.py`: Data classes for representing database schemas (Tables, Columns, Constraints)

### Utils
- `validators.py`: Validation utilities for schema structures

## Data Flow

```
SQL File → Parser → AST Builder → Converter → YAML Output
```

1. User provides SQL DDL file
2. Parser tokenizes and parses SQL statements
3. AST Builder creates structured representation
4. Converter transforms to target format (YAML)
5. Output saved or displayed to user

## Notebook Interface

Jupyter notebooks provide the user interface:
- File upload widgets for SQL input
- Visual feedback during processing
- Download/display of output YAML
