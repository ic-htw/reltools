"""Schema data models.

Data classes representing database schema elements like tables,
columns, constraints, etc.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Column:
    """Represents a database column."""
    name: str
    type: str
    constraints: Optional[str] = None


@dataclass
class ForeignKey:
    """Represents a foreign key constraint."""
    name: str
    columns: List[str]
    ref_table: str
    ref_columns: List[str]


@dataclass
class Table:
    """Represents a database table."""
    name: str
    columns: List[Column]
    primary_key: List[str]
    foreign_keys: List[ForeignKey] = field(default_factory=list)


@dataclass
class Schema:
    """Represents a complete database schema."""
    tables: List[Table]
