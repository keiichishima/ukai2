import xmlrpclib

class UKAIRPCClient(object):
    def __init__(self):
        self._client = None

    def call(self, method, *params):
        # must implement something.
        assert(False)

class UKAIRPCTranslation(object):
    def encode(self, source):
        return source

    def decode(self, souce):
        return source

class UKAIXMLRPCClient(UKAIRPCClient):
    def __init__(self, config):
        super(UKAIXMLRPCClient, self).__init__()
        self._config = config

    def call(self, method, *params):
        if self._client is None:
            self._client = xmlrpclib.ServerProxy(
                'http://%s:%d' % (self._config.get('core_server'),
                                  self._config.get('core_port')),
                allow_none=True)
        try:
            return getattr(self._client, method)(*params)
        except xmlrpclib.Error, e:
            print e.__class__
            del self._client
            self._client = None
            raise

class UKAIXMLRPCTranslation(UKAIRPCTranslation):
    def encode(self, source):
        return xmlrpclib.Binary(source)

    def decode(self, source):
        return source.data
