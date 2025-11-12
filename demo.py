#!/usr/bin/env python3
"""
Demo script for reltools SQL to YAML converter.

This script demonstrates the complete workflow:
1. Parse SQL DDL file
2. Build AST from parsed SQL
3. Convert to YAML format
4. Validate the schema
5. Save YAML output
"""

from pathlib import Path
from src.reltools.parsers.sql_parser import parse_sql_file
from src.reltools.parsers.ast_builder import ASTBuilder
from src.reltools.converters.yaml_converter import ast_to_yaml, save_yaml
from src.reltools.utils.validators import validate_schema, SchemaValidationError
import yaml


def main():
    """Run the complete SQL to YAML conversion demo."""
    print("=" * 60)
    print("SQL DDL to YAML Converter Demo")
    print("=" * 60)

    # Input SQL file
    input_file = Path(__file__).parent / 'tests' / 'fixtures' / 'sample_ddl.sql'
    output_file = Path(__file__).parent / 'data' / 'output' / 'demo_output.yaml'

    print(f"\nStep 1: Reading SQL file: {input_file.name}")
    print("-" * 60)
    with open(input_file, 'r') as f:
        sql_content = f.read()
        print(sql_content)

    # Parse SQL
    print("\nStep 2: Parsing SQL DDL statements")
    print("-" * 60)
    parsed_sql = parse_sql_file(str(input_file))
    print(f"Found {len(parsed_sql['tables'])} tables:")
    for table in parsed_sql['tables']:
        print(f"  - {table['name']} ({len(table['columns'])} columns)")

    # Build AST
    print("\nStep 3: Building Abstract Syntax Tree")
    print("-" * 60)
    builder = ASTBuilder()
    schema = builder.build(parsed_sql)
    print(f"Schema built with {len(schema.tables)} tables")

    # Convert to YAML
    print("\nStep 4: Converting to YAML format")
    print("-" * 60)
    yaml_output = ast_to_yaml(schema)
    print(yaml_output)

    # Validate schema
    print("\nStep 5: Validating schema structure")
    print("-" * 60)
    yaml_data = yaml.safe_load(yaml_output)
    try:
        validate_schema(yaml_data)
        print("✓ Schema validation passed!")
    except SchemaValidationError as e:
        print(f"✗ Schema validation failed: {e}")
        return

    # Save output
    print(f"\nStep 6: Saving output to: {output_file}")
    print("-" * 60)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    save_yaml(yaml_output, str(output_file))
    print(f"✓ YAML file saved successfully!")

    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
