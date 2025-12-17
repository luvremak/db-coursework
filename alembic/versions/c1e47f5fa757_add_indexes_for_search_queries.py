"""add_indexes_for_search_queries

Revision ID: c1e47f5fa757
Revises: 291bc38e926f
Create Date: 2025-12-16 18:14:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1e47f5fa757'
down_revision: Union[str, None] = '291bc38e926f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_company_owner_tg_id', 'company', ['owner_tg_id'])

    op.create_index('ix_project_company_id', 'project', ['company_id'])

    op.create_index('ix_task_assignee_user_id', 'task', ['assignee_user_id'])
    op.create_index('ix_task_project_id', 'task', ['project_id'])
    op.create_index('ix_task_code_project_id', 'task', ['code', 'project_id'])
    op.create_index('ix_task_deadline', 'task', ['deadline'])

    op.create_index('ix_employee_company_id', 'employee', ['company_id'])
    op.create_index('ix_employee_telegram_id_company_id', 'employee', ['telegram_id', 'company_id'])

    op.create_index('ix_time_tracking_entry_task_id_employee_id', 'time_tracking_entry', ['task_id', 'employee_id'])
    op.create_index('ix_time_tracking_entry_created_at', 'time_tracking_entry', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_time_tracking_entry_created_at', table_name='time_tracking_entry')
    op.drop_index('ix_time_tracking_entry_task_id_employee_id', table_name='time_tracking_entry')

    op.drop_index('ix_employee_telegram_id_company_id', table_name='employee')
    op.drop_index('ix_employee_company_id', table_name='employee')

    op.drop_index('ix_task_deadline', table_name='task')
    op.drop_index('ix_task_code_project_id', table_name='task')
    op.drop_index('ix_task_project_id', table_name='task')
    op.drop_index('ix_task_assignee_user_id', table_name='task')

    op.drop_index('ix_project_company_id', table_name='project')

    op.drop_index('ix_company_owner_tg_id', table_name='company')
