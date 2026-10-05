ROLE_ACTIONS = {
    "viewer": {"read"},
    "reporter": {"read", "create"},
    "maintainer": {"read", "create", "close", "reopen"},
}


def require_permission(role: str, action: str) -> None:
    if action not in ROLE_ACTIONS.get(role, set()):
        raise PermissionError(f"Role {role} cannot {action} issues")
