"""Integration tests for complete SQL to YAML workflow."""

import pytest
import yaml
from pathlib import Path
from src.reltools.parsers.sql_parser import parse_sql_file
from src.reltools.parsers.ast_builder import ASTBuilder
from src.reltools.converters.yaml_converter import ast_to_yaml
from src.reltools.utils.validators import validate_schema, SchemaValidationError


def test_full_pipeline_sql_to_yaml():
    """Test complete pipeline from SQL file to YAML."""
    # Parse SQL file
    test_file = Path(__file__).parent / 'fixtures' / 'sample_ddl.sql'
    parsed_sql = parse_sql_file(str(test_file))

    # Build AST
    builder = ASTBuilder()
    schema = builder.build(parsed_sql)

    # Convert to YAML
    yaml_str = ast_to_yaml(schema)

    # Parse YAML and validate
    yaml_data = yaml.safe_load(yaml_str)
    assert validate_schema(yaml_data) is True

    # Verify content
    assert len(yaml_data['tables']) == 2
    assert yaml_data['tables'][0]['name'] == 'users'
    assert yaml_data['tables'][1]['name'] == 'orders'


def test_roundtrip_sql_to_yaml_to_dict():
    """Test roundtrip conversion maintains data integrity."""
    sql = """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        price DECIMAL(10,2) NOT NULL
    );

    CREATE TABLE inventory (
        id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """

    # Parse and build
    from src.reltools.parsers.sql_parser import parse_sql_string

    parsed = parse_sql_string(sql)
    builder = ASTBuilder()
    schema = builder.build(parsed)

    # Convert to YAML and back
    yaml_str = ast_to_yaml(schema)
    yaml_data = yaml.safe_load(yaml_str)

    # Validate
    assert validate_schema(yaml_data) is True

    # Verify data integrity
    assert yaml_data['tables'][0]['name'] == 'products'
    assert yaml_data['tables'][0]['primary_key'] == ['id']
    assert len(yaml_data['tables'][0]['columns']) == 4

    assert yaml_data['tables'][1]['name'] == 'inventory'
    assert len(yaml_data['tables'][1]['foreign_keys']) == 1
    assert yaml_data['tables'][1]['foreign_keys'][0]['ref_table'] == 'products'


def test_expected_yaml_output_format():
    """Test that output matches the expected YAML format from README."""
    test_file = Path(__file__).parent / 'fixtures' / 'sample_ddl.sql'
    expected_file = Path(__file__).parent / 'fixtures' / 'expected_output.yaml'

    # Parse SQL
    parsed_sql = parse_sql_file(str(test_file))

    # Build AST
    builder = ASTBuilder()
    schema = builder.build(parsed_sql)

    # Convert to YAML
    yaml_str = ast_to_yaml(schema)
    actual_data = yaml.safe_load(yaml_str)

    # Load expected output
    with open(expected_file, 'r') as f:
        expected_data = yaml.safe_load(f)

    # Compare structures (note: order matters for lists)
    assert actual_data['tables'][0]['name'] == expected_data['tables'][0]['name']
    assert actual_data['tables'][1]['name'] == expected_data['tables'][1]['name']

    # Validate the actual output
    assert validate_schema(actual_data) is True


def test_parse_validate_invalid_schema():
    """Test that invalid schemas are caught by validator."""
    # Create an intentionally invalid schema (foreign key to non-existent table)
    from src.reltools.converters.yaml_converter import schema_to_dict
    from src.reltools.models.schema import Schema, Table, Column, ForeignKey

    # Create orders table with FK to non-existent users table
    fk = ForeignKey(
        name='fk_invalid',
        columns=['user_id'],
        ref_table='users',  # This table doesn't exist
        ref_columns=['id']
    )

    orders_table = Table(
        name='orders',
        columns=[
            Column(name='id', type='INTEGER'),
            Column(name='user_id', type='INTEGER')
        ],
        primary_key=['id'],
        foreign_keys=[fk]
    )

    schema = Schema(tables=[orders_table])
    schema_dict = schema_to_dict(schema)

    # Validation should fail
    with pytest.raises(SchemaValidationError):
        validate_schema(schema_dict)


def test_composite_keys_integration():
    """Test integration with composite primary and foreign keys."""
    sql = """
    CREATE TABLE course_sections (
        course_id INTEGER,
        section_id INTEGER,
        instructor VARCHAR(100),
        PRIMARY KEY (course_id, section_id)
    );

    CREATE TABLE enrollments (
        student_id INTEGER,
        course_id INTEGER,
        section_id INTEGER,
        grade VARCHAR(2),
        PRIMARY KEY (student_id, course_id, section_id),
        FOREIGN KEY (course_id, section_id) REFERENCES course_sections(course_id, section_id)
    );
    """

    from src.reltools.parsers.sql_parser import parse_sql_string

    parsed = parse_sql_string(sql)
    builder = ASTBuilder()
    schema = builder.build(parsed)
    yaml_str = ast_to_yaml(schema)
    yaml_data = yaml.safe_load(yaml_str)

    # Validate
    assert validate_schema(yaml_data) is True

    # Check composite primary key
    assert yaml_data['tables'][0]['primary_key'] == ['course_id', 'section_id']
    assert yaml_data['tables'][1]['primary_key'] == ['student_id', 'course_id', 'section_id']

    # Check composite foreign key
    fk = yaml_data['tables'][1]['foreign_keys'][0]
    assert fk['columns'] == ['course_id', 'section_id']
    assert fk['ref_columns'] == ['course_id', 'section_id']
