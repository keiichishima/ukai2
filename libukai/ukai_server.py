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

import msgpackrpc
from SimpleXMLRPCServer import SimpleXMLRPCServer
import SocketServer
import xmlrpclib

from ukai_core import UKAICore, UKAI_CONFIG_FILE_DEFAULT

class AsyncSimpleXMLRPCServer(SocketServer.ThreadingMixIn,
                              SimpleXMLRPCServer):
    pass

def main2():
    try:
        core = UKAICore(config_file=UKAI_CONFIG_FILE_DEFAULT)
        server = msgpackrpc.Server(core)
        server.listen(msgpackrpc.Address(core.core_server,
                                         core.core_port))
        server.start()
    except KeyboardInterrupt, e:
        pass

def main():
    try:
        core = UKAICore(config_file=UKAI_CONFIG_FILE_DEFAULT)
        server = AsyncSimpleXMLRPCServer((core.core_server,
                                          core.core_port),
                                         logRequests=False,
                                         allow_none=True)
        server.register_instance(core)
        server.serve_forever()
    except KeyboardInterrupt, e:
        pass


main()