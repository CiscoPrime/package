SUPPORTED_RESOURCES = {
    "tacacs_policies": {
        "path": "admin/rs/uiapi/policytable/tacacs",
        "method": "GET",
        "requires_csrf": False,
        "params": []  # No extra parameters for this request
    },
    "sync_action": {
        "path": "admin/syncupAction.do",
        "method": "POST",
        "requires_csrf": True,
        "params": ["hostname"]  # `hostname` is a required parameter
    }
}
