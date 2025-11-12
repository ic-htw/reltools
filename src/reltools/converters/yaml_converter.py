"""YAML converter module.

Converts AST representations to YAML format.
"""

import yaml
from typing import Dict, Any, Union
from ..models.schema import Schema


def ast_to_yaml(ast: Union[Schema, Dict[str, Any]]) -> str:
    """
    Convert an AST to YAML format.

    Args:
        ast: Abstract syntax tree representation (Schema object or dict)

    Returns:
        YAML string representation
    """
    # Convert Schema object to dictionary if needed
    if isinstance(ast, Schema):
        schema_dict = schema_to_dict(ast)
    else:
        schema_dict = ast

    # Convert to YAML with proper formatting
    yaml_str = yaml.dump(
        schema_dict,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        indent=2
    )

    return yaml_str


def schema_to_dict(schema: Schema) -> Dict[str, Any]:
    """
    Convert a Schema object to a dictionary suitable for YAML export.

    Args:
        schema: Schema object

    Returns:
        Dictionary representation
    """
    tables_list = []

    for table in schema.tables:
        table_dict = {
            'name': table.name,
            'columns': []
        }

        # Add columns
        for col in table.columns:
            col_dict = {
                'name': col.name,
                'type': col.type
            }
            if col.constraints:
                col_dict['constraints'] = col.constraints
            table_dict['columns'].append(col_dict)

        # Add primary key
        table_dict['primary_key'] = table.primary_key

        # Add foreign keys if present
        if table.foreign_keys:
            table_dict['foreign_keys'] = []
            for fk in table.foreign_keys:
                fk_dict = {
                    'name': fk.name,
                    'columns': fk.columns,
                    'ref_table': fk.ref_table,
                    'ref_columns': fk.ref_columns
                }
                table_dict['foreign_keys'].append(fk_dict)

        tables_list.append(table_dict)

    return {'tables': tables_list}


def save_yaml(yaml_content: str, filepath: str) -> None:
    """
    Save YAML content to a file.

    Args:
        yaml_content: YAML string to save
        filepath: Destination file path
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
