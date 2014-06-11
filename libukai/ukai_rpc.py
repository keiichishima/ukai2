# Copyright 2014
# IIJ Innovation Institute Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
# 
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above
#   copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials
#   provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY IIJ INNOVATION INSTITUTE INC. ``AS
# IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL IIJ INNOVATION INSTITUTE INC. OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.

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
