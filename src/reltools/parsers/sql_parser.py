"""SQL DDL parser module.

Parses SQL DDL statements (CREATE TABLE, etc.) and converts them
into an abstract syntax tree representation.
"""

import re
from typing import Dict, List, Any
import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DDL, Name


def parse_sql_file(filepath: str) -> Dict[str, Any]:
    """
    Parse a SQL file containing DDL statements.

    Args:
        filepath: Path to the SQL file

    Returns:
        Dictionary representing the parsed SQL structure
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    return parse_sql_string(sql_content)


def parse_sql_string(sql_content: str) -> Dict[str, Any]:
    """
    Parse a string containing SQL DDL statements.

    Args:
        sql_content: String containing SQL DDL

    Returns:
        Dictionary representing the parsed SQL structure with tables list
    """
    statements = sqlparse.parse(sql_content)
    tables = []

    for stmt in statements:
        print(stmt.get_type())
        if stmt.get_type() == 'CREATE':
            table_def = _parse_create_table(stmt)
            if table_def:
                tables.append(table_def)

    return {'tables': tables}


def _parse_create_table(stmt: Statement) -> Dict[str, Any]:
    """
    Parse a CREATE TABLE statement.

    Args:
        stmt: Parsed SQL statement

    Returns:
        Dictionary with table definition
    """
    tokens = list(stmt.flatten())
    table_name = None
    columns = []
    primary_key = []
    foreign_keys = []

    # Find table name
    in_table_name = False
    for token in tokens:
        if token.ttype is DDL and token.value.upper() == 'CREATE':
            continue
        if token.ttype is Keyword and token.value.upper() == 'TABLE':
            in_table_name = True
            continue
        if in_table_name and token.ttype is Name and not token.is_whitespace:
            table_name = token.value.strip('`"[]')
            break

    # Parse column definitions and constraints
    stmt_str = str(stmt)

    # Extract content between parentheses
    paren_match = re.search(r'\((.*)\)', stmt_str, re.DOTALL)
    if paren_match:
        definitions = paren_match.group(1)

        # Split by commas (but not within parentheses)
        parts = _split_by_comma(definitions)

        for part in parts:
            part = part.strip()

            # Check for PRIMARY KEY constraint
            if re.match(r'PRIMARY\s+KEY', part, re.IGNORECASE):
                pk_match = re.search(r'PRIMARY\s+KEY\s*\(([^)]+)\)', part, re.IGNORECASE)
                if pk_match:
                    pk_cols = [col.strip().strip('`"[]') for col in pk_match.group(1).split(',')]
                    primary_key.extend(pk_cols)

            # Check for FOREIGN KEY constraint
            elif re.match(r'FOREIGN\s+KEY', part, re.IGNORECASE):
                fk_def = _parse_foreign_key(part)
                if fk_def:
                    foreign_keys.append(fk_def)

            # Check for CONSTRAINT with named foreign key
            elif re.match(r'CONSTRAINT', part, re.IGNORECASE):
                fk_def = _parse_foreign_key(part)
                if fk_def:
                    foreign_keys.append(fk_def)

            # Parse column definition
            else:
                col_def = _parse_column_definition(part)
                if col_def:
                    columns.append(col_def)
                    # Check for inline PRIMARY KEY
                    if col_def.get('is_primary_key'):
                        primary_key.append(col_def['name'])

    if not table_name:
        return None

    return {
        'name': table_name,
        'columns': columns,
        'primary_key': primary_key,
        'foreign_keys': foreign_keys
    }


def _parse_column_definition(col_def: str) -> Dict[str, Any]:
    """
    Parse a column definition.

    Args:
        col_def: Column definition string

    Returns:
        Dictionary with column information
    """
    # Match column_name datatype [constraints]
    parts = col_def.split(None, 2)

    if len(parts) < 2:
        return None

    col_name = parts[0].strip('`"[]')
    col_type = parts[1].upper()

    # Check for type with parameters like VARCHAR(50)
    type_match = re.match(r'([A-Z]+)(\([^)]+\))?', parts[1], re.IGNORECASE)
    if type_match:
        col_type = type_match.group(0).upper()

    constraints = None
    is_primary_key = False

    if len(parts) > 2:
        constraints_str = parts[2].strip()
        # Check for PRIMARY KEY
        if re.search(r'PRIMARY\s+KEY', constraints_str, re.IGNORECASE):
            is_primary_key = True
            # Remove PRIMARY KEY from constraints string
            constraints_str = re.sub(r'PRIMARY\s+KEY', '', constraints_str, flags=re.IGNORECASE).strip()

        if constraints_str:
            constraints = constraints_str

    return {
        'name': col_name,
        'type': col_type,
        'constraints': constraints,
        'is_primary_key': is_primary_key
    }


def _parse_foreign_key(fk_def: str) -> Dict[str, Any]:
    """
    Parse a foreign key definition.

    Args:
        fk_def: Foreign key definition string

    Returns:
        Dictionary with foreign key information
    """
    # Extract constraint name if present
    name_match = re.search(r'CONSTRAINT\s+([^\s]+)', fk_def, re.IGNORECASE)
    fk_name = name_match.group(1).strip('`"[]') if name_match else None

    # Extract FOREIGN KEY columns
    fk_cols_match = re.search(r'FOREIGN\s+KEY\s*\(([^)]+)\)', fk_def, re.IGNORECASE)
    if not fk_cols_match:
        return None

    fk_columns = [col.strip().strip('`"[]') for col in fk_cols_match.group(1).split(',')]

    # Extract REFERENCES table and columns
    ref_match = re.search(r'REFERENCES\s+([^\s(]+)\s*\(([^)]+)\)', fk_def, re.IGNORECASE)
    if not ref_match:
        return None

    ref_table = ref_match.group(1).strip('`"[]')
    ref_columns = [col.strip().strip('`"[]') for col in ref_match.group(2).split(',')]

    # Generate a name if not provided
    if not fk_name:
        fk_name = f"fk_{ref_table}_{'_'.join(fk_columns)}"

    return {
        'name': fk_name,
        'columns': fk_columns,
        'ref_table': ref_table,
        'ref_columns': ref_columns
    }


def _split_by_comma(text: str) -> List[str]:
    """
    Split text by commas, but not within parentheses.

    Args:
        text: Text to split

    Returns:
        List of parts
    """
    parts = []
    current = []
    paren_depth = 0

    for char in text:
        if char == '(':
            paren_depth += 1
            current.append(char)
        elif char == ')':
            paren_depth -= 1
            current.append(char)
        elif char == ',' and paren_depth == 0:
            parts.append(''.join(current))
            current = []
        else:
            current.append(char)

    if current:
        parts.append(''.join(current))

    return parts
