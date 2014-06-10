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
The ukai_node_error_state.py module provides classes to store node
failure status and a set of failure status class instances.
'''

import time
import threading

class UKAINodeErrorStateSet(object):
    '''
    The UKAINodeErrorStateSet class provides interfaces to manage
    the list of failure node list.
    '''
    def __init__(self):
        '''
        Initializes a internal dictionary object to keep
        UKAINodeErrorState class instances, and a lock object.

        Return values: This function does not return any values.
        '''
        self._set = {}
        self._lock = threading.Lock()

    def add(self, address, reason):
        '''
        Creates a UKAINodeErrorState instance from the specified
        node address and reason value, and insert the instance to
        the internal dictionary object.

        address: The IP address of the failure node.
        reason: The reason value of the failure.

        Return values: This function does not return any values.
        '''
        try:
            self._lock.acquire()
            self._set[address] = UKAINodeErrorState(address, reason)
        finally:
            self._lock.release()
        
    def is_in_failure(self, address):
        '''
        Returns True if the specified node is listed in the
        internal failure node dictionary object.  Otherwise
        returns False.

        address: The IP address of the node to be checked.

        Return values: True if the specified node is in the
            failure node dictionary object, False otherwise.
        '''
        try:
            self._lock.acquire()
            if address not in self._set:
                return (False)
            # Check if retry timer is expired or not.
            if self._set[address].is_expired() is True:
                # If timer is expired, then remove the entry
                # from the failure node list.
                del self._set[address]
                return (False)
            return (True)

        finally:
            self._lock.release()

    def get_list(self):
        '''
        Returns a list of nodes and its status in the failure node
        list.

        Return values: A list object of a dictionary object of
        following format.

            {
                'address': NODE_ADDRESS,
                'reason': FAILURE_REASON,
                'retry_after': RETRY_TIME
            }

        Currently NODE_ADDRESS will be in the IPv4 printable string
        format.  FAILURE_REASON is always 0.  RETRY_TIME indicates
        expiration time of this entry to be removed.  Once the entry
        is removed from the list, the UKAI system will try to contact
        the node again.
        '''
        try:
            self._lock.acquire()
            copied_set = []
            for address in self._set:
                state = self._set[address]
                copied_set.append({'address': state.address,
                                   'reason': state.reason,
                                   'retry_after': state.retry_after
                                   })
            return (copied_set)

        finally:
            self._lock.release()
        
class UKAINodeErrorState(object):
    '''
    The UKAINodeErrorState class represents the node information
    which is considered in a failure status.
    '''
    def __init__(self, address, reason):
        '''
        Initializes an instance of the UKAINodeErrorState class
        with the specifided node address and reason value.

        address: The IP address of the failed node.
        reason: The reason value of the failure.

        Return values: This function does not return any values.
        '''
        # The failure state is cached for 60 seconds.
        self._suspend_time = 60
        self._address = address
        self._reason = reason
        self._retry_after = time.time() + self._suspend_time

    @property
    def address(self):
        '''
        The IP address of the failed node.
        '''
        return (self._address)

    @property
    def reason(self):
        '''
        The reason of the failure.
        '''
        return (self._reason)

    @property
    def retry_after(self):
        '''
        The expiration time of this entry.  The UKAI system tries to
        contact this node again after this timer has expired.
        '''
        return (self._retry_after)

    def is_expired(self):
        '''
        Returns True if the expiration timer of this entry has expired.

        Return values: True if the timer has expired, False otherwise.
        '''
        return (self._retry_after < time.time())

    def extend(self, reason):
        '''
        Extends the expiration timer.

        Return values: This function does not return any values.
        '''
        self._reason = reason
        self._retry_after = time.time() + self._suspend_time
