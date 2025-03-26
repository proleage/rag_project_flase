from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from flask import request
from flask_login import UserMixin  # type: ignore
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from configs import rag_config
from models.base import Base

from .engine import db
from .enums import CreatedByRole
from .types import StringUUID


class App(Base):
    __tablename__ = "apps"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="app_pkey"),
        db.Index("app_tenant_id_idx", "tenant_id"),
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))
    tenant_id: Mapped[str] = db.Column(StringUUID, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(
        db.Text, nullable=False, server_default=db.text("''::character varying")
    )
    mode: Mapped[str] = mapped_column(db.String(255), nullable=False)
    icon_type = db.Column(db.String(255), nullable=True)  # image, emoji
    icon = db.Column(db.String(255))
    icon_background = db.Column(db.String(255))
    app_model_config_id = db.Column(StringUUID, nullable=True)
    workflow_id = db.Column(StringUUID, nullable=True)
    status = db.Column(
        db.String(255),
        nullable=False,
        server_default=db.text("'normal'::character varying"),
    )
    enable_site = db.Column(db.Boolean, nullable=False)
    enable_api = db.Column(db.Boolean, nullable=False)
    api_rpm = db.Column(db.Integer, nullable=False, server_default=db.text("0"))
    api_rph = db.Column(db.Integer, nullable=False, server_default=db.text("0"))
    is_demo = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    is_public = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    is_universal = db.Column(
        db.Boolean, nullable=False, server_default=db.text("false")
    )
    tracing = db.Column(db.Text, nullable=True)
    max_active_requests: Mapped[Optional[int]] = mapped_column(nullable=True)
    created_by = db.Column(StringUUID, nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, server_default=func.current_timestamp()
    )
    updated_by = db.Column(StringUUID, nullable=True)
    updated_at = db.Column(
        db.DateTime, nullable=False, server_default=func.current_timestamp()
    )
    use_icon_as_answer_icon = db.Column(
        db.Boolean, nullable=False, server_default=db.text("false")
    )



    @property
    def api_base_url(self):
        return (rag_config.SERVICE_API_URL or request.host_url.rstrip("/")) + "/v1"


class EndUser(Base, UserMixin):
    __tablename__ = "end_users"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="end_user_pkey"),
        db.Index("end_user_session_id_idx", "session_id", "type"),
        db.Index("end_user_tenant_session_id_idx", "tenant_id", "session_id", "type"),
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))
    tenant_id = db.Column(StringUUID, nullable=False)
    app_id = db.Column(StringUUID, nullable=True)
    type = db.Column(db.String(255), nullable=False)
    external_user_id = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255))
    is_anonymous = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))
    session_id: Mapped[str] = mapped_column()
    created_at = db.Column(
        db.DateTime, nullable=False, server_default=func.current_timestamp()
    )
    updated_at = db.Column(
        db.DateTime, nullable=False, server_default=func.current_timestamp()
    )


class UploadFile(Base):
    __tablename__ = "upload_files"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="upload_file_pkey"),
        db.Index("upload_file_tenant_idx", "tenant_id"),
    )

    id: Mapped[str] = db.Column(
        StringUUID, server_default=db.text("uuid_generate_v4()")
    )
    tenant_id: Mapped[str] = db.Column(StringUUID, nullable=False)
    storage_type: Mapped[str] = db.Column(db.String(255), nullable=False)
    key: Mapped[str] = db.Column(db.String(255), nullable=False)
    name: Mapped[str] = db.Column(db.String(255), nullable=False)
    size: Mapped[int] = db.Column(db.Integer, nullable=False)
    extension: Mapped[str] = db.Column(db.String(255), nullable=False)
    mime_type: Mapped[str] = db.Column(db.String(255), nullable=True)
    created_by_role: Mapped[str] = db.Column(
        db.String(255),
        nullable=False,
        server_default=db.text("'account'::character varying"),
    )
    created_by: Mapped[str] = db.Column(StringUUID, nullable=False)
    created_at: Mapped[datetime] = db.Column(
        db.DateTime, nullable=False, server_default=func.current_timestamp()
    )
    used: Mapped[bool] = db.Column(
        db.Boolean, nullable=False, server_default=db.text("false")
    )
    used_by: Mapped[str | None] = db.Column(StringUUID, nullable=True)
    used_at: Mapped[datetime | None] = db.Column(db.DateTime, nullable=True)
    hash: Mapped[str | None] = db.Column(db.String(255), nullable=True)
    source_url: Mapped[str] = mapped_column(sa.TEXT, default="")

    def __init__(
        self,
        *,
        tenant_id: str,
        storage_type: str,
        key: str,
        name: str,
        size: int,
        extension: str,
        mime_type: str,
        created_by_role: CreatedByRole,
        created_by: str,
        created_at: datetime,
        used: bool,
        used_by: str | None = None,
        used_at: datetime | None = None,
        hash: str | None = None,
        source_url: str = "",
    ):
        self.tenant_id = tenant_id
        self.storage_type = storage_type
        self.key = key
        self.name = name
        self.size = size
        self.extension = extension
        self.mime_type = mime_type
        self.created_by_role = created_by_role.value
        self.created_by = created_by
        self.created_at = created_at
        self.used = used
        self.used_by = used_by
        self.used_at = used_at
        self.hash = hash
        self.source_url = source_url

class RagSetup(Base):
    __tablename__ = "dify_setups"
    __table_args__ = (db.PrimaryKeyConstraint("version", name="dify_setup_pkey"),)

    version = db.Column(db.String(255), nullable=False)
    setup_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())