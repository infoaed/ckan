import urllib

import paste.fixture

from ckanclient import CkanClient, CkanApiError
try:
    from ckanclient import ApiRequest
except ImportError:
    # older versions of ckanclient
    from ckanclient import Request as ApiRequest

__all__ = ['WsgiCkanClient', 'ClientError']

__version__ = '0.5'

class ClientError(Exception):
    pass

class WsgiCkanClient(CkanClient):
    '''Same as CkanClient, but instead of requests going through urllib,
    they are passed directly to an application\'s Paste (webtest/wsgi)
    interface.'''
    def __init__(self, app, **kwargs):
        self.app = app
        super(WsgiCkanClient, self).__init__(**kwargs)
        CkanClient._open_url = self.open_url

    def open_url(self, location, data=None, headers={}, method=None):
        self.last_location = location

        if data != None:
            data = urllib.urlencode({data: 1})
        # Don't use request beyond getting the method
        req = ApiRequest(location, data, headers, method=method)

        # Make header values ascii strings
        for key, value in headers.items():
            headers[key] = str('%s' % value)

        method = req.get_method()
        kwargs = {'status':'*', 'headers':headers}
        try:
            if method == 'GET':
                assert not data
                res = self.app.get(location, **kwargs)
            elif method == 'POST':
                res = self.app.post(location, data, **kwargs)
            elif method == 'PUT':
                res = self.app.put(location, data, **kwargs)
            elif method == 'DELETE':
                assert not data
                res = self.app.delete(location, **kwargs)
            else:
                raise ClientError('No Paste interface for method \'%s\': %s' % \
                                  (method, location))
        except paste.fixture.AppError, inst:
            self.last_http_error = inst
            self.last_status = 500
            self.last_message = repr(inst.args)
        else:
            if res.status not in (200, 201):
                self.last_http_error = res
                self.last_status = res.status
                self.last_message = res.body
            else:
                self.last_status = res.status
                self.last_body = res.body
                self.last_headers = dict(res.headers)
                content_type = self.last_headers['Content-Type']
                is_json_response = False
                if 'json' in content_type:
                    is_json_response = True
                if is_json_response:
                    self.last_message = self._loadstr(self.last_body)
                else:
                    self.last_message = self.last_body
        if self.last_status not in (200, 201):
            raise CkanApiError(self.last_message)
