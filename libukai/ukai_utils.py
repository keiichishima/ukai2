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
The ukai_utils.py module provides a set of general functions to other
UKAI modules.
'''

import netifaces
import time

from ukai_config import UKAIConfig

ukai_config = UKAIConfig()

UKAIIfaddrCache = {
    'expiration_time': 0,
    'cached_addrs': [],
}
UKAI_IFADDR_CACHE_VALID_TIME = 1

def UKAIIsLocalNode(node):
    '''
    The UKAIIsLocalNode function checks if the node is a local node or
    not by comparing the passed value and all the addresses assigned
    to local network interfaces.
    '''
    now = time.time()

    if (ukai_config.get('ifaddr_cache') is True):
        # ifaddr cache is enabled.
        if UKAIIfaddrCache['expiration_time'] > now:
            return (node in UKAIIfaddrCache['cached_addrs'])

    UKAIIfaddrCache['cached_addrs'] = []
    for interface in netifaces.interfaces():
        ifaddresses = netifaces.ifaddresses(interface)
        for family in ifaddresses.keys():
            for addr in ifaddresses[family]:
                UKAIIfaddrCache['cached_addrs'].append(addr['addr'])
    UKAIIfaddrCache['expiration_time'] = (now
                                          + UKAI_IFADDR_CACHE_VALID_TIME)

    return (node in UKAIIfaddrCache['cached_addrs'])
