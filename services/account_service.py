from datetime import UTC, datetime, timedelta
from typing import Any, Optional, cast

from pydantic import BaseModel
from werkzeug.exceptions import Unauthorized

from configs import rag_config
from extensions.ext_database import db
from libs.helper import RateLimiter
from models.account import Account, AccountStatus, TenantAccountJoin


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


REFRESH_TOKEN_PREFIX = "refresh_token:"
ACCOUNT_REFRESH_TOKEN_PREFIX = "account_refresh_token:"
REFRESH_TOKEN_EXPIRY = timedelta(days=rag_config.REFRESH_TOKEN_EXPIRE_DAYS)


class AccountService:
    reset_password_rate_limiter = RateLimiter(
        prefix="reset_password_rate_limit", max_attempts=1, time_window=60 * 1
    )
    email_code_login_rate_limiter = RateLimiter(
        prefix="email_code_login_rate_limit", max_attempts=1, time_window=60 * 1
    )
    email_code_account_deletion_rate_limiter = RateLimiter(
        prefix="email_code_account_deletion_rate_limit",
        max_attempts=1,
        time_window=60 * 1,
    )
    LOGIN_MAX_ERROR_LIMITS = 5
    FORGOT_PASSWORD_MAX_ERROR_LIMITS = 5

    @staticmethod
    def load_user(user_id: str) -> None | Account:
        account = db.session.query(Account).filter_by(id=user_id).first()
        if not account:
            return None

        if account.status == AccountStatus.BANNED.value:
            raise Unauthorized("Account is banned.")

        current_tenant = TenantAccountJoin.query.filter_by(
            account_id=account.id, current=True
        ).first()
        if current_tenant:
            account.current_tenant_id = current_tenant.tenant_id
        else:
            available_ta = (
                TenantAccountJoin.query.filter_by(account_id=account.id)
                .order_by(TenantAccountJoin.id.asc())
                .first()
            )
            if not available_ta:
                return None

            account.current_tenant_id = available_ta.tenant_id
            available_ta.current = True
            db.session.commit()

        if datetime.now(UTC).replace(tzinfo=None) - account.last_active_at > timedelta(
            minutes=10
        ):
            account.last_active_at = datetime.now(UTC).replace(tzinfo=None)
            db.session.commit()

        return cast(Account, account)

    @staticmethod
    def load_logged_in_account(*, account_id: str):
        return AccountService.load_user(account_id)
