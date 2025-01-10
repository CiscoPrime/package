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
<<<<<<< Updated upstream
        "requires_csrf": False,
=======
        "requires_csrf": True,
>>>>>>> Stashed changes
        "params": [],  # No extra parameters for this request
        "headers": {
            "_QPH_": "cXVlcnk9c3lzdGVtU3VtbWFyeQ=="
        }  # No custom headers needed for this request
<<<<<<< Updated upstream
    },
    "context": {
        "path": "admin/rs/uiapi/visibility",
        "method": "GET",
        "requires_csrf": False,
        "params": [],  # No extra parameters for this request
        "headers": {
            "_QPH_": "ZmlsdGVyQ3JpdGVyaWE9JTdCJTIycHJlZGljYXRlJTIyJTNBJTIyYWxsJTIyJTJDJTIyY29uZGl0aW9ucyUyMiUzQSU1QiU3QiUyMmF0dHIlMjIlM0ElMjJJZGVudGl0eUdyb3VwJTIyJTJDJTIyb3BlcmF0b3IlMjIlM0ElMjJub3QtY29udGFpbnMlMjIlMkMlMjJ2YWx1ZSUyMiUzQSUyMkhPLUNpc2NvLUFQcyUyMiU3RCUyQyU3QiUyMmF0dHIlMjIlM0ElMjJFbmRQb2ludFBvbGljeSUyMiUyQyUyMm9wZXJhdG9yJTIyJTNBJTIyY29udGFpbnMlMjIlMkMlMjJ2YWx1ZSUyMiUzQSUyMmNpc2NvLWFwJTIyJTdEJTVEJTdEJkVuZFBvaW50UG9saWN5PWNpc2NvLWFwJmNvbHVtbnM9TUFDQWRkcmVzcyUyQ0VuZFBvaW50UHJvZmlsZXJTZXJ2ZXIlMkNzdGF0dXMlMkNob3N0LW5hbWUlMkN1c2VyTmFtZSUyQ05ldHdvcmtEZXZpY2VOYW1lJTJDTkFTLVBvcnQtSWQlMkNFbmRQb2ludFBvbGljeSUyQ0lkZW50aXR5R3JvdXAlMkNMb2NhdGlvbiUyQ0ZhaWx1cmVSZWFzb24lMkNBbGxvd2VkUHJvdG9jb2xNYXRjaGVkUnVsZSUyQ0F1dGhvcml6YXRpb25Qb2xpY3lNYXRjaGVkUnVsZSUyQ0F1dGhlbnRpY2F0aW9uTWV0aG9kJTJDRW5kUG9pbnRHcm91cCUyQ0F1dGhlbnRpY2F0aW9uSWRlbnRpdHlTdG9yZSUyQ0RldmljZSUyMFR5cGUlMkNpcCZzb3J0Qnk9TUFDQWRkcmVzcyZzdGFydEF0PTEmcGFnZVNpemU9MTAmdG90YWxfcGFnZXM9NjI4MCZ0b3RhbF9lbnRyaWVzPTYyNzk4"
        }  # No custom headers needed for this request
    },
    "Broken_APs": {
        "path": "admin/rs/uiapi/visibility",
        "method": "GET",
        "requires_csrf": False,
        "params": [],  # No extra parameters for this request
        "headers": {
            "_QPH_": "ZmlsdGVyQ3JpdGVyaWE9JTdCJTIycHJlZGljYXRlJTIyJTNBJTIyYWxsJTIyJTJDJTIyY29uZGl0aW9ucyUyMiUzQSU1QiU3QiUyMmF0dHIlMjIlM0ElMjJFbmRQb2ludFBvbGljeSUyMiUyQyUyMm9wZXJhdG9yJTIyJTNBJTIyY29udGFpbnMlMjIlMkMlMjJ2YWx1ZSUyMiUzQSUyMmNpc2NvLWFwJTIyJTdEJTVEJTdEJkVuZFBvaW50UG9saWN5PWNpc2NvLWFwJmNvbHVtbnM9TUFDQWRkcmVzcyUyQ0VuZFBvaW50UG9saWN5JTJDSWRlbnRpdHlHcm91cCZzb3J0Qnk9TUFDQWRkcmVzcyZzdGFydEF0PTEmcGFnZVNpemU9MzAwMCZ0b3RhbF9wYWdlcz0zMTcmdG90YWxfZW50cmllcz0zMTcw"
        }  # No custom headers needed for this request
=======
>>>>>>> Stashed changes
    }
}