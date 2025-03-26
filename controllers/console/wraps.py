import json
import os
import time
from functools import wraps

from flask import abort, request
from flask_login import current_user  # type: ignore

from configs import rag_config
from controllers.console.workspace.error import AccountNotInitializedError
from extensions.ext_database import db

from models.model import RagSetup
# from services.feature_service import FeatureService

from .error import NotInitValidateError, NotSetupError, UnauthorizedAndForceLogout


def account_initialization_required(view):
    @wraps(view)
    def decorated(*args, **kwargs):
        # check account initialization
        account = current_user

        if account.status == "uninitialized":
            raise AccountNotInitializedError()

        return view(*args, **kwargs)

    return decorated


# def cloud_edition_billing_resource_check(resource: str):
#     def interceptor(view):
#         @wraps(view)
#         def decorated(*args, **kwargs):
#             features = FeatureService.get_features(current_user.current_tenant_id)
#             if features.billing.enabled:
#                 members = features.members
#                 apps = features.apps
#                 vector_space = features.vector_space
#                 documents_upload_quota = features.documents_upload_quota
#                 annotation_quota_limit = features.annotation_quota_limit
#                 if resource == "members" and 0 < members.limit <= members.size:
#                     abort(403, "The number of members has reached the limit of your subscription.")
#                 elif resource == "apps" and 0 < apps.limit <= apps.size:
#                     abort(403, "The number of apps has reached the limit of your subscription.")
#                 elif resource == "vector_space" and 0 < vector_space.limit <= vector_space.size:
#                     abort(
#                         403, "The capacity of the knowledge storage space has reached the limit of your subscription."
#                     )
#                 elif resource == "documents" and 0 < documents_upload_quota.limit <= documents_upload_quota.size:
#                     # The api of file upload is used in the multiple places,
#                     # so we need to check the source of the request from datasets
#                     source = request.args.get("source")
#                     if source == "datasets":
#                         abort(403, "The number of documents has reached the limit of your subscription.")
#                     else:
#                         return view(*args, **kwargs)
#                 elif resource == "workspace_custom" and not features.can_replace_logo:
#                     abort(403, "The workspace custom feature has reached the limit of your subscription.")
#                 elif resource == "annotation" and 0 < annotation_quota_limit.limit < annotation_quota_limit.size:
#                     abort(403, "The annotation quota has reached the limit of your subscription.")
#                 else:
#                     return view(*args, **kwargs)
#
#             return view(*args, **kwargs)
#
#         return decorated
#
#     return interceptor



def setup_required(view):
    @wraps(view)
    def decorated(*args, **kwargs):
        # check setup
        if (
            rag_config.EDITION == "SELF_HOSTED"
            and os.environ.get("INIT_PASSWORD")
            and not db.session.query(RagSetup).first()
        ):
            raise NotInitValidateError()
        elif rag_config.EDITION == "SELF_HOSTED" and not db.session.query(RagSetup).first():
            raise NotSetupError()

        return view(*args, **kwargs)

    return decorated

