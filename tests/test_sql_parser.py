"""Tests for SQL parser module."""

import pytest
from pathlib import Path
from src.reltools.parsers.sql_parser import parse_sql_file, parse_sql_string


def test_parse_sql_file():
    """Test parsing a SQL file."""
    test_file = Path(__file__).parent / 'fixtures' / 'sample_ddl.sql'
    result = parse_sql_file(str(test_file))

    assert 'tables' in result
    assert len(result['tables']) == 2

    # Check users table
    users_table = result['tables'][0]
    assert users_table['name'] == 'users'
    assert len(users_table['columns']) == 3
    assert users_table['primary_key'] == ['id']

    # Check columns
    assert users_table['columns'][0]['name'] == 'id'
    assert users_table['columns'][0]['type'] == 'INTEGER'
    assert users_table['columns'][1]['name'] == 'username'
    assert users_table['columns'][1]['type'] == 'VARCHAR(50)'
    assert users_table['columns'][1]['constraints'] == 'NOT NULL'

    # Check orders table
    orders_table = result['tables'][1]
    assert orders_table['name'] == 'orders'
    assert len(orders_table['columns']) == 5
    assert orders_table['primary_key'] == ['id']
    assert len(orders_table['foreign_keys']) == 1

    # Check foreign key
    fk = orders_table['foreign_keys'][0]
    assert fk['columns'] == ['user_id']
    assert fk['ref_table'] == 'users'
    assert fk['ref_columns'] == ['id']


def test_parse_sql_string():
    """Test parsing a SQL string."""
    sql = """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        price DECIMAL(10,2)
    );
    """

    result = parse_sql_string(sql)

    assert 'tables' in result
    assert len(result['tables']) == 1

    table = result['tables'][0]
    assert table['name'] == 'products'
    assert len(table['columns']) == 3
    assert table['primary_key'] == ['id']

    # Check columns
    assert table['columns'][0]['name'] == 'id'
    assert table['columns'][0]['type'] == 'INTEGER'
    assert table['columns'][1]['name'] == 'name'
    assert table['columns'][1]['constraints'] == 'NOT NULL'
    assert table['columns'][2]['name'] == 'price'
    assert table['columns'][2]['type'] == 'DECIMAL(10,2)'


def test_parse_multiple_tables():
    """Test parsing multiple CREATE TABLE statements."""
    sql = """
    CREATE TABLE authors (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL
    );

    CREATE TABLE books (
        id INTEGER PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        author_id INTEGER NOT NULL,
        FOREIGN KEY (author_id) REFERENCES authors(id)
    );
    """

    result = parse_sql_string(sql)

    assert len(result['tables']) == 2
    assert result['tables'][0]['name'] == 'authors'
    assert result['tables'][1]['name'] == 'books'

    # Check foreign key in books
    books = result['tables'][1]
    assert len(books['foreign_keys']) == 1
    fk = books['foreign_keys'][0]
    assert fk['ref_table'] == 'authors'


def test_parse_composite_primary_key():
    """Test parsing a composite primary key."""
    sql = """
    CREATE TABLE enrollment (
        student_id INTEGER,
        course_id INTEGER,
        enrollment_date DATE,
        PRIMARY KEY (student_id, course_id)
    );
    """

    result = parse_sql_string(sql)

    table = result['tables'][0]
    assert table['name'] == 'enrollment'
    assert table['primary_key'] == ['student_id', 'course_id']


def test_parse_inline_primary_key():
    """Test parsing inline PRIMARY KEY constraint."""
    sql = """
    CREATE TABLE categories (
        id INTEGER PRIMARY KEY,
        name VARCHAR(50)
    );
    """

    result = parse_sql_string(sql)

    table = result['tables'][0]
    assert table['name'] == 'categories'
    assert table['primary_key'] == ['id']
