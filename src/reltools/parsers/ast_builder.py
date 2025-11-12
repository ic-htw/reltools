"""AST builder module.

Constructs abstract syntax tree representations from parsed SQL.
"""

from typing import Dict, Any
from ..models.schema import Schema, Table, Column, ForeignKey


class ASTBuilder:
    """Builds an AST from parsed SQL tokens."""

    def __init__(self):
        """Initialize the AST builder."""
        pass

    def build(self, parsed_sql: Dict[str, Any]) -> Schema:
        """
        Build an AST from parsed SQL.

        Args:
            parsed_sql: Parsed SQL structure (dict with 'tables' key)

        Returns:
            Schema object representing the database schema
        """
        tables = []

        for table_dict in parsed_sql.get('tables', []):
            table = self._build_table(table_dict)
            tables.append(table)

        return Schema(tables=tables)

    def _build_table(self, table_dict: Dict[str, Any]) -> Table:
        """
        Build a Table object from parsed table dictionary.

        Args:
            table_dict: Dictionary with table information

        Returns:
            Table object
        """
        columns = []
        for col_dict in table_dict.get('columns', []):
            # Remove 'is_primary_key' as it's not part of the Column model
            col_data = {
                'name': col_dict['name'],
                'type': col_dict['type'],
                'constraints': col_dict.get('constraints')
            }
            column = Column(**col_data)
            columns.append(column)

        foreign_keys = []
        for fk_dict in table_dict.get('foreign_keys', []):
            foreign_key = ForeignKey(
                name=fk_dict['name'],
                columns=fk_dict['columns'],
                ref_table=fk_dict['ref_table'],
                ref_columns=fk_dict['ref_columns']
            )
            foreign_keys.append(foreign_key)

        return Table(
            name=table_dict['name'],
            columns=columns,
            primary_key=table_dict.get('primary_key', []),
            foreign_keys=foreign_keys
        )
