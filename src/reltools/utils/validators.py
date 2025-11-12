"""Validation utilities for schema structures."""

from typing import Dict, Any, List, Set


class SchemaValidationError(Exception):
    """Exception raised when schema validation fails."""
    pass


def validate_schema(schema: Dict[str, Any]) -> bool:
    """
    Validate a schema dictionary structure.

    Args:
        schema: Schema dictionary to validate

    Returns:
        True if valid

    Raises:
        SchemaValidationError: If schema is invalid
    """
    if not isinstance(schema, dict):
        raise SchemaValidationError("Schema must be a dictionary")

    if 'tables' not in schema:
        raise SchemaValidationError("Schema must have 'tables' key")

    tables = schema['tables']
    if not isinstance(tables, list):
        raise SchemaValidationError("'tables' must be a list")

    # Collect all table names for foreign key validation
    table_names = set()
    table_columns = {}  # table_name -> set of column names

    # First pass: validate tables and collect names/columns
    for i, table in enumerate(tables):
        _validate_table(table, i)
        table_names.add(table['name'])
        table_columns[table['name']] = {col['name'] for col in table['columns']}

    # Second pass: validate foreign key references
    for table in tables:
        _validate_foreign_keys(table, table_names, table_columns)

    return True


def _validate_table(table: Dict[str, Any], index: int) -> None:
    """
    Validate a single table definition.

    Args:
        table: Table dictionary
        index: Table index in the list

    Raises:
        SchemaValidationError: If table is invalid
    """
    if not isinstance(table, dict):
        raise SchemaValidationError(f"Table at index {index} must be a dictionary")

    # Check required fields
    if 'name' not in table:
        raise SchemaValidationError(f"Table at index {index} must have 'name' field")

    if 'columns' not in table:
        raise SchemaValidationError(f"Table '{table['name']}' must have 'columns' field")

    if 'primary_key' not in table:
        raise SchemaValidationError(f"Table '{table['name']}' must have 'primary_key' field")

    # Validate name
    if not isinstance(table['name'], str) or not table['name']:
        raise SchemaValidationError(f"Table name at index {index} must be a non-empty string")

    # Validate columns
    columns = table['columns']
    if not isinstance(columns, list):
        raise SchemaValidationError(f"Table '{table['name']}' columns must be a list")

    if not columns:
        raise SchemaValidationError(f"Table '{table['name']}' must have at least one column")

    column_names = set()
    for col_idx, column in enumerate(columns):
        _validate_column(column, table['name'], col_idx)
        if column['name'] in column_names:
            raise SchemaValidationError(
                f"Duplicate column name '{column['name']}' in table '{table['name']}'"
            )
        column_names.add(column['name'])

    # Validate primary key
    primary_key = table['primary_key']
    if not isinstance(primary_key, list):
        raise SchemaValidationError(f"Table '{table['name']}' primary_key must be a list")

    for pk_col in primary_key:
        if pk_col not in column_names:
            raise SchemaValidationError(
                f"Primary key column '{pk_col}' not found in table '{table['name']}'"
            )


def _validate_column(column: Dict[str, Any], table_name: str, index: int) -> None:
    """
    Validate a single column definition.

    Args:
        column: Column dictionary
        table_name: Name of the parent table
        index: Column index in the list

    Raises:
        SchemaValidationError: If column is invalid
    """
    if not isinstance(column, dict):
        raise SchemaValidationError(
            f"Column at index {index} in table '{table_name}' must be a dictionary"
        )

    # Check required fields
    if 'name' not in column:
        raise SchemaValidationError(
            f"Column at index {index} in table '{table_name}' must have 'name' field"
        )

    if 'type' not in column:
        raise SchemaValidationError(
            f"Column '{column.get('name', f'at index {index}')}' in table '{table_name}' "
            f"must have 'type' field"
        )

    # Validate name
    if not isinstance(column['name'], str) or not column['name']:
        raise SchemaValidationError(
            f"Column name at index {index} in table '{table_name}' must be a non-empty string"
        )

    # Validate type
    if not isinstance(column['type'], str) or not column['type']:
        raise SchemaValidationError(
            f"Column '{column['name']}' type in table '{table_name}' must be a non-empty string"
        )

    # Validate constraints if present
    if 'constraints' in column and column['constraints'] is not None:
        if not isinstance(column['constraints'], str):
            raise SchemaValidationError(
                f"Column '{column['name']}' constraints in table '{table_name}' must be a string"
            )


def _validate_foreign_keys(
    table: Dict[str, Any],
    table_names: Set[str],
    table_columns: Dict[str, Set[str]]
) -> None:
    """
    Validate foreign key definitions in a table.

    Args:
        table: Table dictionary
        table_names: Set of all table names in the schema
        table_columns: Dict mapping table names to their column names

    Raises:
        SchemaValidationError: If foreign keys are invalid
    """
    if 'foreign_keys' not in table:
        return

    foreign_keys = table['foreign_keys']
    if not isinstance(foreign_keys, list):
        raise SchemaValidationError(f"Table '{table['name']}' foreign_keys must be a list")

    for fk_idx, fk in enumerate(foreign_keys):
        _validate_foreign_key(fk, table, fk_idx, table_names, table_columns)


def _validate_foreign_key(
    fk: Dict[str, Any],
    table: Dict[str, Any],
    index: int,
    table_names: Set[str],
    table_columns: Dict[str, Set[str]]
) -> None:
    """
    Validate a single foreign key definition.

    Args:
        fk: Foreign key dictionary
        table: Parent table dictionary
        index: Foreign key index
        table_names: Set of all table names
        table_columns: Dict mapping table names to column names

    Raises:
        SchemaValidationError: If foreign key is invalid
    """
    table_name = table['name']

    if not isinstance(fk, dict):
        raise SchemaValidationError(
            f"Foreign key at index {index} in table '{table_name}' must be a dictionary"
        )

    # Check required fields
    required_fields = ['name', 'columns', 'ref_table', 'ref_columns']
    for field in required_fields:
        if field not in fk:
            raise SchemaValidationError(
                f"Foreign key at index {index} in table '{table_name}' must have '{field}' field"
            )

    # Validate name
    if not isinstance(fk['name'], str) or not fk['name']:
        raise SchemaValidationError(
            f"Foreign key name at index {index} in table '{table_name}' must be a non-empty string"
        )

    # Validate columns
    if not isinstance(fk['columns'], list) or not fk['columns']:
        raise SchemaValidationError(
            f"Foreign key '{fk['name']}' columns in table '{table_name}' must be a non-empty list"
        )

    for col in fk['columns']:
        if col not in table_columns[table_name]:
            raise SchemaValidationError(
                f"Foreign key '{fk['name']}' references non-existent column '{col}' "
                f"in table '{table_name}'"
            )

    # Validate ref_table
    if not isinstance(fk['ref_table'], str) or not fk['ref_table']:
        raise SchemaValidationError(
            f"Foreign key '{fk['name']}' ref_table in table '{table_name}' "
            f"must be a non-empty string"
        )

    if fk['ref_table'] not in table_names:
        raise SchemaValidationError(
            f"Foreign key '{fk['name']}' in table '{table_name}' references "
            f"non-existent table '{fk['ref_table']}'"
        )

    # Validate ref_columns
    if not isinstance(fk['ref_columns'], list) or not fk['ref_columns']:
        raise SchemaValidationError(
            f"Foreign key '{fk['name']}' ref_columns in table '{table_name}' "
            f"must be a non-empty list"
        )

    for col in fk['ref_columns']:
        if col not in table_columns[fk['ref_table']]:
            raise SchemaValidationError(
                f"Foreign key '{fk['name']}' in table '{table_name}' references "
                f"non-existent column '{col}' in table '{fk['ref_table']}'"
            )

    # Validate that columns and ref_columns have same length
    if len(fk['columns']) != len(fk['ref_columns']):
        raise SchemaValidationError(
            f"Foreign key '{fk['name']}' in table '{table_name}' has mismatched "
            f"column counts: {len(fk['columns'])} columns but {len(fk['ref_columns'])} ref_columns"
        )
