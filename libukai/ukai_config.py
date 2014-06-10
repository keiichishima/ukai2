# Copyright 2013, 2014
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

'''
The ukai_config.py module defines the global parameters of the
UKAI system.

metadata_root: the location of the backend metadata storage space.
data_root: the location of the backend image storage space.
blockname_format: the filename format of each block data.
proxy_port: the listening port of the UKAI system to receive
    remote read/write operations.
'''

import json
import re

DEFAULT_CONFIG_FILE = '/etc/ukai/config'

comment_re = re.compile('^\s*#.*$', re.MULTILINE)

class UKAIConfig(object):
    def __init__(self, config_file=DEFAULT_CONFIG_FILE):
        config_content = ''
        with open(config_file) as fp:
            config_content = ''.join(fp.readlines())
            match = comment_re.search(config_content)
            while match:
                config_content = (config_content[:match.start()]
                                  + config_content[match.end():])
                match = comment_re.search(config_content)
                
        self._config = json.loads(config_content)

    def get(self, param):
        if param in self._config:
            return (self._config[param])
        else:
            return (None)

    def set(self, param, value):
        self._config[param] = value

if __name__ == '__main__':
    config = UKAIConfig()
    print config._config
