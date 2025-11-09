"""Seed predefined roles and defect statuses

Revision ID: 002
Revises: 001
Create Date: 2024-11-09 12:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Text, Integer

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Define table structures for bulk insert
    roles_table = table(
        'roles',
        column('id', Integer),
        column('name', String),
        column('description', Text)
    )
    
    defect_statuses_table = table(
        'defect_statuses',
        column('id', Integer),
        column('name', String),
        column('description', Text)
    )
    
    # Insert predefined roles
    # Requirements: 2.1 - Engineer, Manager, Observer, Admin
    op.bulk_insert(
        roles_table,
        [
            {
                'id': 1,
                'name': 'Engineer',
                'description': 'Can create defects, add comments, attach files, and modify their own defects'
            },
            {
                'id': 2,
                'name': 'Manager',
                'description': 'Can assign executors, change defect statuses, generate reports, and manage projects'
            },
            {
                'id': 3,
                'name': 'Observer',
                'description': 'Can view projects, defects, and reports without modification rights'
            },
            {
                'id': 4,
                'name': 'Admin',
                'description': 'Full access to manage users, roles, projects, and security settings'
            }
        ]
    )
    
    # Insert predefined defect statuses
    # Requirements: 6.1 - New, In Progress, Review, Closed, Canceled
    op.bulk_insert(
        defect_statuses_table,
        [
            {
                'id': 1,
                'name': 'New',
                'description': 'Defect has been created and is awaiting assignment'
            },
            {
                'id': 2,
                'name': 'In Progress',
                'description': 'Defect is currently being worked on'
            },
            {
                'id': 3,
                'name': 'Review',
                'description': 'Defect fix is complete and awaiting review'
            },
            {
                'id': 4,
                'name': 'Closed',
                'description': 'Defect has been resolved and verified'
            },
            {
                'id': 5,
                'name': 'Canceled',
                'description': 'Defect has been canceled and will not be fixed'
            }
        ]
    )
    
    # Update sequences to continue from the last inserted ID
    op.execute("SELECT setval('roles_id_seq', 4, true)")
    op.execute("SELECT setval('defect_statuses_id_seq', 5, true)")


def downgrade() -> None:
    # Delete predefined data in reverse order
    op.execute("DELETE FROM defect_statuses WHERE id IN (1, 2, 3, 4, 5)")
    op.execute("DELETE FROM roles WHERE id IN (1, 2, 3, 4)")
    
    # Reset sequences
    op.execute("SELECT setval('roles_id_seq', 1, false)")
    op.execute("SELECT setval('defect_statuses_id_seq', 1, false)")
