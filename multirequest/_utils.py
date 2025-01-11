def _dispatch_request(session, http_method):
    return {
        'GET': session.get,
        'DELETE': session.delete,
        'PUT': session.put,
        'POST': session.post,
        'PATCH': session.patch,
    }.get(http_method, 'GET')
