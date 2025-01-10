SUPPORTED_RESOURCES = {
    "tacacs_policies": {
        "path": "admin/rs/uiapi/policytable/tacacs",
        "method": "GET",
        "requires_csrf": False,
        "params": [],  # No extra parameters for this request
        "headers": {}  # No custom headers needed for this request
    },
    "sync_action": {
        "path": "admin/syncupAction.do",
        "method": "POST",
        "requires_csrf": True,
        "params": ["hostname"],  # `hostname` is a required parameter
        "headers": {
            "_QPH_": "Y29tbWFuZD1zeW5jdXBEQg==",  # Special header specific to `sync_action`
            "X-Requested-With": "XMLHttpRequest"  # Resource-specific header for sync
        }
    },
    "radius_policies": {
        "path": "admin/rs/uiapi/policytable/radius",
        "method": "GET",
        "requires_csrf": False,
        "params": [],  # No extra parameters for this request
        "headers": {}  # No custom headers needed for this request
    },
    "system_summary": {
        "path": "admin/rs/uiapi/dashboard/generic/fetchData",
        "method": "GET",
        "requires_csrf": True,
        "params": [],  # No extra parameters for this request
        "headers": {
            "_QPH_": "cXVlcnk9c3lzdGVtU3VtbWFyeQ=="
        }  # No custom headers needed for this request
    }
}