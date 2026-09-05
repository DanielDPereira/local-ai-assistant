"""Módulo de segurança do agente."""

from assistant.security.audit import AuditTrail
from assistant.security.destructive import DestructiveOperationPolicy
from assistant.security.secrets import SecretProtection
from assistant.security.workspace import WorkspaceBoundary, WorkspaceBoundaryError

__all__ = [
    "AuditTrail",
    "DestructiveOperationPolicy",
    "SecretProtection",
    "WorkspaceBoundary",
    "WorkspaceBoundaryError",
]
