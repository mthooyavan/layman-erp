from rest_framework.response import Response


def handle(message, status=400, code=None):
    error_response = {"error": {
        "status": status,
        "code": code,
        "message": message
    }}
    return Response(error_response, status=status)
