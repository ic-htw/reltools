"""Tests for YAML converter module."""

import pytest
import yaml
import tempfile
from pathlib import Path
from src.reltools.converters.yaml_converter import ast_to_yaml, save_yaml, schema_to_dict
from src.reltools.models.schema import Schema, Table, Column, ForeignKey


def test_ast_to_yaml_from_schema_object():
    """Test AST to YAML conversion from Schema object."""
    # Create a schema with tables
    column1 = Column(name='id', type='INTEGER')
    column2 = Column(name='name', type='VARCHAR(50)', constraints='NOT NULL')

    table = Table(
        name='users',
        columns=[column1, column2],
        primary_key=['id'],
        foreign_keys=[]
    )

    schema = Schema(tables=[table])

    # Convert to YAML
    yaml_str = ast_to_yaml(schema)

    # Parse back to verify structure
    data = yaml.safe_load(yaml_str)

    assert 'tables' in data
    assert len(data['tables']) == 1
    assert data['tables'][0]['name'] == 'users'
    assert len(data['tables'][0]['columns']) == 2
    assert data['tables'][0]['columns'][0]['name'] == 'id'
    assert data['tables'][0]['columns'][1]['constraints'] == 'NOT NULL'
    assert data['tables'][0]['primary_key'] == ['id']


def test_ast_to_yaml_with_foreign_keys():
    """Test YAML conversion with foreign keys."""
    # Create users table
    users_table = Table(
        name='users',
        columns=[Column(name='id', type='INTEGER')],
        primary_key=['id']
    )

    # Create orders table with foreign key
    fk = ForeignKey(
        name='fk_orders_user',
        columns=['user_id'],
        ref_table='users',
        ref_columns=['id']
    )

    orders_table = Table(
        name='orders',
        columns=[
            Column(name='id', type='INTEGER'),
            Column(name='user_id', type='INTEGER', constraints='NOT NULL')
        ],
        primary_key=['id'],
        foreign_keys=[fk]
    )

    schema = Schema(tables=[users_table, orders_table])
    yaml_str = ast_to_yaml(schema)

    # Parse and verify
    data = yaml.safe_load(yaml_str)

    orders = data['tables'][1]
    assert orders['name'] == 'orders'
    assert 'foreign_keys' in orders
    assert len(orders['foreign_keys']) == 1

    fk_data = orders['foreign_keys'][0]
    assert fk_data['name'] == 'fk_orders_user'
    assert fk_data['columns'] == ['user_id']
    assert fk_data['ref_table'] == 'users'
    assert fk_data['ref_columns'] == ['id']


def test_ast_to_yaml_from_dict():
    """Test AST to YAML conversion from dictionary."""
    schema_dict = {
        'tables': [
            {
                'name': 'products',
                'columns': [
                    {'name': 'id', 'type': 'INTEGER'},
                    {'name': 'price', 'type': 'DECIMAL(10,2)'}
                ],
                'primary_key': ['id']
            }
        ]
    }

    yaml_str = ast_to_yaml(schema_dict)
    data = yaml.safe_load(yaml_str)

    assert data == schema_dict


def test_schema_to_dict():
    """Test converting Schema object to dictionary."""
    column = Column(name='id', type='INTEGER', constraints='PRIMARY KEY')
    table = Table(name='test', columns=[column], primary_key=['id'])
    schema = Schema(tables=[table])

    result = schema_to_dict(schema)

    assert isinstance(result, dict)
    assert 'tables' in result
    assert result['tables'][0]['name'] == 'test'
    assert result['tables'][0]['columns'][0]['name'] == 'id'


def test_schema_to_dict_omits_none_constraints():
    """Test that None constraints are not included in output."""
    column = Column(name='id', type='INTEGER')  # No constraints
    table = Table(name='test', columns=[column], primary_key=['id'])
    schema = Schema(tables=[table])

    result = schema_to_dict(schema)

    # Constraint field should not be present if None
    col_dict = result['tables'][0]['columns'][0]
    assert 'name' in col_dict
    assert 'type' in col_dict
    assert 'constraints' not in col_dict or col_dict.get('constraints') is None


def test_save_yaml():
    """Test saving YAML to file."""
    yaml_content = "tables:\n  - name: test\n"

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        temp_path = f.name

    try:
        save_yaml(yaml_content, temp_path)

        # Read back and verify
        with open(temp_path, 'r') as f:
            content = f.read()

        assert content == yaml_content
    finally:
        Path(temp_path).unlink()


def test_yaml_output_matches_expected_format():
    """Test that YAML output matches the expected format from README."""
    # Create the exact structure from README example
    users_table = Table(
        name='users',
        columns=[
            Column(name='id', type='INTEGER'),
            Column(name='username', type='VARCHAR(50)', constraints='NOT NULL'),
            Column(name='email', type='VARCHAR(100)', constraints='NOT NULL')
        ],
        primary_key=['id']
    )

    fk = ForeignKey(
        name='fk_orders_user',
        columns=['user_id'],
        ref_table='users',
        ref_columns=['id']
    )

    orders_table = Table(
        name='orders',
        columns=[
            Column(name='id', type='INTEGER'),
            Column(name='user_id', type='INTEGER', constraints='NOT NULL'),
            Column(name='user_email', type='VARCHAR(100)', constraints='NOT NULL'),
            Column(name='order_date', type='DATETIME', constraints='NOT NULL'),
            Column(name='total', type='DECIMAL(10,2)')
        ],
        primary_key=['id'],
        foreign_keys=[fk]
    )

    schema = Schema(tables=[users_table, orders_table])
    yaml_str = ast_to_yaml(schema)

    # Parse and verify structure matches README format
    data = yaml.safe_load(yaml_str)

    assert 'tables' in data
    assert data['tables'][0]['name'] == 'users'
    assert data['tables'][1]['name'] == 'orders'
    assert data['tables'][1]['foreign_keys'][0]['name'] == 'fk_orders_user'
