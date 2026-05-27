"""empty message

Revision ID: 001
Revises:
Create Date: 2026-05-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create content table
    op.create_table(
        'content',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sentence_id', sa.Integer(), nullable=False, comment='文案库序号(1-150)'),
        sa.Column('text', sa.Text(), nullable=False, comment='文案内容'),
        sa.Column('image_url', sa.String(length=255), nullable=True, comment='图片URL'),
        sa.Column('logo_version', sa.String(length=20), nullable=True, comment='logo版本(原色/反白)'),
        sa.Column('status', sa.Enum('待审核', '已通过', '已拒绝', '已发布', name='contentstatus'), nullable=False, comment='状态'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='创建时间'),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True, comment='审核时间'),
        sa.Column('published_at', sa.DateTime(), nullable=True, comment='发布时间'),
        sa.Column('reviewer_id', sa.Integer(), nullable=True, comment='审核人ID'),
        sa.Column('reject_reason', sa.Text(), nullable=True, comment='拒绝原因'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_id'), 'content', ['id'], unique=False)
    op.create_index('idx_status', 'content', ['status'], unique=False)
    op.create_index('idx_sentence_id', 'content', ['sentence_id'], unique=False)

    # Create publish_log table
    op.create_table(
        'publish_log',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('weibo_id', sa.String(length=50), nullable=True, comment='微博ID'),
        sa.Column('status', sa.Enum('成功', '失败', name='publishstatus'), nullable=False, comment='发布状态'),
        sa.Column('error_msg', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('published_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True, comment='发布时间'),
        sa.ForeignKeyConstraint(['content_id'], ['content.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_publish_log_id'), 'publish_log', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_publish_log_id'), table_name='publish_log')
    op.drop_table('publish_log')
    op.drop_index('idx_sentence_id', table_name='content')
    op.drop_index('idx_status', table_name='content')
    op.drop_index(op.f('ix_content_id'), table_name='content')
    op.drop_table('content')
