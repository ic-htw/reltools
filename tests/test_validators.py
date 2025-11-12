"""Tests for schema validation module."""

import pytest
from src.reltools.utils.validators import validate_schema, SchemaValidationError


def test_validate_valid_schema():
    """Test validation of a valid schema."""
    schema = {
        'tables': [
            {
                'name': 'users',
                'columns': [
                    {'name': 'id', 'type': 'INTEGER'},
                    {'name': 'name', 'type': 'VARCHAR(50)', 'constraints': 'NOT NULL'}
                ],
                'primary_key': ['id']
            }
        ]
    }

    assert validate_schema(schema) is True


def test_validate_schema_missing_tables_key():
    """Test validation fails when 'tables' key is missing."""
    schema = {'foo': 'bar'}

    with pytest.raises(SchemaValidationError, match="must have 'tables' key"):
        validate_schema(schema)


def test_validate_schema_not_dict():
    """Test validation fails when schema is not a dictionary."""
    with pytest.raises(SchemaValidationError, match="must be a dictionary"):
        validate_schema("not a dict")


def test_validate_tables_not_list():
    """Test validation fails when tables is not a list."""
    schema = {'tables': 'not a list'}

    with pytest.raises(SchemaValidationError, match="must be a list"):
        validate_schema(schema)


def test_validate_table_missing_name():
    """Test validation fails when table lacks name."""
    schema = {
        'tables': [
            {
                'columns': [{'name': 'id', 'type': 'INTEGER'}],
                'primary_key': ['id']
            }
        ]
    }

    with pytest.raises(SchemaValidationError, match="must have 'name' field"):
        validate_schema(schema)


def test_validate_table_missing_columns():
    """Test validation fails when table lacks columns."""
    schema = {
        'tables': [
            {
                'name': 'users',
                'primary_key': ['id']
            }
        ]
    }

    with pytest.raises(SchemaValidationError, match="must have 'columns' field"):
        validate_schema(schema)


def test_validate_table_missing_primary_key():
    """Test validation fails when table lacks primary_key."""
    schema = {
        'tables': [
            {
                'name': 'users',
                'columns': [{'name': 'id', 'type': 'INTEGER'}]
            }
        ]
    }

    with pytest.raises(SchemaValidationError, match="must have 'primary_key' field"):
        validate_schema(schema)


def test_validate_column_missing_name():
    """Test validation fails when column lacks name."""
    schema = {
        'tables': [
            {
                'name': 'users',
                'columns': [{'type': 'INTEGER'}],
                'primary_key': []
            }
        ]
    }

    with pytest.raises(SchemaValidationError, match="must have 'name' field"):
        validate_schema(schema)


def test_validate_column_missing_type():
    """Test validation fails when column lacks type."""
    schema = {
        'tables': [
            {
                'name': 'users',
                'columns': [{'name': 'id'}],
                'primary_key': []
            }
        ]
    }

    with pytest.raises(SchemaValidationError, match="must have 'type' field"):
        validate_schema(schema)


def test_validate_duplicate_column_names():
    """Test validation fails with duplicate column names."""
    schema = {
        'tables': [
            {
                'name': 'users',
                'columns': [
                    {'name': 'id', 'type': 'INTEGER'},
                    {'name': 'id', 'type': 'VARCHAR(50)'}
                ],
                'primary_key': ['id']
            }
        ]
    }

    with pytest.raises(SchemaValidationError, match="Duplicate column name"):
        validate_schema(schema)


def test_validate_primary_key_references_nonexistent_column():
    """Test validation fails when primary key references non-existent column."""
    schema = {
        'tables': [
            {
                'name': 'users',
                'columns': [{'name': 'id', 'type': 'INTEGER'}],
                'primary_key': ['nonexistent']
            }
        ]
    }

    with pytest.raises(SchemaValidationError, match="Primary key column .* not found"):
        validate_schema(schema)


def test_validate_foreign_key_references_nonexistent_table():
    """Test validation fails when foreign key references non-existent table."""
    schema = {
        'tables': [
            {
                'name': 'orders',
                'columns': [
                    {'name': 'id', 'type': 'INTEGER'},
                    {'name': 'user_id', 'type': 'INTEGER'}
                ],
                'primary_key': ['id'],
                'foreign_keys': [
                    {
                        'name': 'fk_user',
                        'columns': ['user_id'],
                        'ref_table': 'users',
                        'ref_columns': ['id']
                    }
                ]
            }
        ]
    }

    with pytest.raises(SchemaValidationError, match="references non-existent table"):
        validate_schema(schema)


def test_validate_foreign_key_references_nonexistent_column():
    """Test validation fails when foreign key references non-existent column."""
    schema = {
        'tables': [
            {
                'name': 'users',
                'columns': [{'name': 'id', 'type': 'INTEGER'}],
                'primary_key': ['id']
            },
            {
                'name': 'orders',
                'columns': [
                    {'name': 'id', 'type': 'INTEGER'},
                    {'name': 'user_id', 'type': 'INTEGER'}
                ],
                'primary_key': ['id'],
                'foreign_keys': [
                    {
                        'name': 'fk_user',
                        'columns': ['user_id'],
                        'ref_table': 'users',
                        'ref_columns': ['nonexistent']
                    }
                ]
            }
        ]
    }

    with pytest.raises(SchemaValidationError, match="references non-existent column"):
        validate_schema(schema)


def test_validate_foreign_key_local_column_doesnt_exist():
    """Test validation fails when foreign key local column doesn't exist."""
    schema = {
        'tables': [
            {
                'name': 'users',
                'columns': [{'name': 'id', 'type': 'INTEGER'}],
                'primary_key': ['id']
            },
            {
                'name': 'orders',
                'columns': [{'name': 'id', 'type': 'INTEGER'}],
                'primary_key': ['id'],
                'foreign_keys': [
                    {
                        'name': 'fk_user',
                        'columns': ['nonexistent_col'],
                        'ref_table': 'users',
                        'ref_columns': ['id']
                    }
                ]
            }
        ]
    }

    with pytest.raises(SchemaValidationError, match="references non-existent column"):
        validate_schema(schema)


def test_validate_foreign_key_mismatched_column_counts():
    """Test validation fails when foreign key has mismatched column counts."""
    schema = {
        'tables': [
            {
                'name': 'users',
                'columns': [
                    {'name': 'id', 'type': 'INTEGER'},
                    {'name': 'email', 'type': 'VARCHAR(100)'}
                ],
                'primary_key': ['id']
            },
            {
                'name': 'orders',
                'columns': [
                    {'name': 'id', 'type': 'INTEGER'},
                    {'name': 'user_id', 'type': 'INTEGER'}
                ],
                'primary_key': ['id'],
                'foreign_keys': [
                    {
                        'name': 'fk_user',
                        'columns': ['user_id'],
                        'ref_table': 'users',
                        'ref_columns': ['id', 'email']  # Mismatch: 1 vs 2
                    }
                ]
            }
        ]
    }

    with pytest.raises(SchemaValidationError, match="mismatched column counts"):
        validate_schema(schema)


def test_validate_complex_valid_schema():
    """Test validation of a complex valid schema with multiple tables and foreign keys."""
    schema = {
        'tables': [
            {
                'name': 'users',
                'columns': [
                    {'name': 'id', 'type': 'INTEGER'},
                    {'name': 'username', 'type': 'VARCHAR(50)', 'constraints': 'NOT NULL'},
                    {'name': 'email', 'type': 'VARCHAR(100)', 'constraints': 'NOT NULL'}
                ],
                'primary_key': ['id']
            },
            {
                'name': 'orders',
                'columns': [
                    {'name': 'id', 'type': 'INTEGER'},
                    {'name': 'user_id', 'type': 'INTEGER', 'constraints': 'NOT NULL'},
                    {'name': 'total', 'type': 'DECIMAL(10,2)'}
                ],
                'primary_key': ['id'],
                'foreign_keys': [
                    {
                        'name': 'fk_orders_user',
                        'columns': ['user_id'],
                        'ref_table': 'users',
                        'ref_columns': ['id']
                    }
                ]
            }
        ]
    }

    assert validate_schema(schema) is True
