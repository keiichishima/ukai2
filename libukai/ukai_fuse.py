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

import errno
import sys

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

from ukai_config import UKAIConfig
from ukai_core import UKAI_CONFIG_FILE_DEFAULT
from ukai_rpc import UKAIXMLRPCClient, UKAIXMLRPCTranslation

class UKAIFUSE(LoggingMixIn, Operations):
    ''' UKAI FUSE connector.
    '''

    def __init__(self, config_file):
        self._fd = 0
        self._config = UKAIConfig(config_file)
        self._rpc_client = UKAIXMLRPCClient(self._config)
        self._rpc_trans = UKAIXMLRPCTranslation()

    def init(self, path):
        ''' Initializing code.
        '''
        pass

    def destroy(self, path):
        ''' Cleanup code.
        '''
        pass

    def chmod(self, path, mode):
        return 0

    def chown(self, path, uid, gid):
        return 0

    def create(self, path, mode):
        return errno.EPERM

    def getattr(self, path, fh=None):
        (ret, st) = self._rpc_client.call('getattr', path)
        if ret != 0:
            raise FuseOSError(ret)
        return st

    def mkdir(self, path, mode):
        return errno.EPERM

    def open(self, path, flags):
        ret = self._rpc_client.call('open', path, flags)
        if ret != 0:
            raise FuseOSError(ret)
        self._fd += 1
        return self._fd

    def release(self, path, fh):
        self._rpc_client.call('release', path)
        return 0

    def read(self, path, size, offset, fh):
        # UKAI core returns the data as RPC safe encoded data.
        ret, encoded_data = self._rpc_client.call('read', path,
                                                  size, offset)
        if ret != 0:
            raise FuseOSError(ret)
        return self._rpc_trans.decode(encoded_data)

    def readdir(self, path, fh):
        return self._rpc_client.call('readdir', path)

    def readlink(self, path):
        return errno.EPERM

    def rename(self, old, new):
        return errno.EPERM

    def rmdir(self, path):
        return errno.EPERM

    def statfs(self, path):
        return self._rpc_client.call('statfs', path)

    def symlink(self, target, source):
        return errno.EPERM

    def truncate(self, path, length, fh=None):
        #return errno.EPERM
        pass

    def unlink(self, path):
        return errno.EPERM

    def utimens(self, path, times=None):
        pass

    def write(self, path, data, offset, fh):
        # need to convert data to UKAI Core as a RPC safe
        # encoded data.
        encoded_data = self._rpc_trans.encode(data)
        ret, nwritten = self._rpc_client.call('write', path,
                                              encoded_data, offset)
        if ret != 0:
            raise FuseOSError(ret)
        return nwritten

def main():
    import getopt

    if len(sys.argv) < 2:
        print '''Usage %s [-fd] MOUNTPOINT
\t-f: run in foreground.
\t-d: output debug information.''' % sys.argv[0]
        sys.exit(-1)

    fuse_foreground = False
    fuse_debug = False
    config_file = UKAI_CONFIG_FILE_DEFAULT
    (optlist, args) = getopt.getopt(sys.argv[1:], 'fdc:')
    for opt_pair in optlist:
        if opt_pair[0] == '-f':
            fuse_foreground = True
        if opt_pair[0] == '-d':
            fuse_debug = True
        if opt_pair[0] == '-c':
            config_file = opt_pair[1]
    mountpoint = args[0]

    FUSE(UKAIFUSE(config_file), mountpoint,
         foreground=fuse_foreground,
         debug=fuse_debug,
         nothreads=True, # XXX to avoid parallel XMLRPC messages.
         allow_other=True)

if __name__ == '__main__':
    main()
