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
import json
import stat
import sys
import zlib

from ukai_config import UKAIConfig
from ukai_data import UKAIData
from ukai_local_io import ukai_local_read, ukai_local_write
from ukai_local_io import ukai_local_allocate_dataspace
from ukai_metadata import UKAIMetadata, UKAI_OUT_OF_SYNC
from ukai_metadata import ukai_metadata_create
from ukai_node_error_state import UKAINodeErrorStateSet
from ukai_rpc import UKAIXMLRPCTranslation
from ukai_statistics import UKAIStatistics, UKAIImageStatistics

UKAI_CONFIG_FILE_DEFAULT = '/etc/ukai/config'

class UKAICore(object):
    ''' UKAI core processing.
    '''

    def __init__(self, config):
        self._metadata_dict = {}
        self._data_dict = {}
        self._config = config
        self._node_error_state_set = UKAINodeErrorStateSet()
        self._open_image_set = set()
        self._rpc_trans = UKAIXMLRPCTranslation()

    @property
    def metadata_server(self):
        return self._config.get('metadata_server')

    @property
    def core_server(self):
        return self._config.get('core_server')

    @property
    def core_port(self):
        return self._config.get('core_port')

    ''' Filesystem I/O processing.
    '''
    def getattr(self, path):
        ret = 0
        st = None
        if path == '/':
            st = dict(st_mode=(stat.S_IFDIR | 0755), st_ctime=0,
                      st_mtime=0, st_atime=0, st_nlink=2)
        else:
            image_name = path[1:]
            if self._exists(image_name):
                st = dict(st_mode=(stat.S_IFREG | 0644), st_ctime=0,
                          st_mtime=0, st_atime=0, st_nlink=1,
                          st_size=self._metadata_dict[image_name].size)
            else:
                ret = errno.ENOENT
        return ret, st

    def open(self, path, flags):
        ret = 0
        image_name = path[1:]
        if not self._exists(image_name):
            return errno.ENOENT
        if image_name in self._open_image_set:
            return errno.EBUSY
        else:
            self._open_image_set.add(image_name)

        return 0

    def release(self, path):
        image_name = path[1:]
        if image_name in self._open_image_set:
            self._open_image_set.remove(image_name)
        return 0

    def read(self, path, size, offset):
        image_name = path[1:]
        if not self._exists(image_name):
            return errno.ENOENT, None
        image_data = self._data_dict[image_name]
        data = image_data.read(size, offset)
        return 0, self._rpc_trans.encode(data)

    def readdir(self, path):
        return ['.', '..'] + self._metadata_dict.keys()

    def statfs(self, path):
        ''' TODO: the values are fake right now.
        '''
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def truncate(self, path, length):
        return errno.EPERM

    def unlink(self, path):
        return errno.EPERM

    def write(self, path, encoded_data, offset):
        image_name = path[1:]
        if not self._exists(image_name):
            return errno.ENOENT, None
        image_data = self._data_dict[image_name]
        return 0, image_data.write(self._rpc_trans.decode(encoded_data),
                                   offset)

    def _exists(self, image_name):
        if image_name not in self._metadata_dict:
            return False
        if image_name not in self._data_dict:
            return False
        return True


    ''' Proxy server processing.
    '''
    def proxy_read(self, image_name, block_size, block_index, offset,
                   size):
        data = ukai_local_read(image_name, block_size, block_index,
                               offset, size, self._config)
        return self._rpc_trans.encode(zlib.compress(data))

    def proxy_write(self, image_name, block_size, block_index, offset,
                    encoded_data):
        data = zlib.decompress(self._rpc_trans.decode(encoded_data))
        return ukai_local_write(image_name, block_size, block_index,
                                offset, data, self._config)

    def proxy_allocate_dataspace(self, image_name, block_size, block_index):
        return ukai_local_allocate_dataspace(image_name, block_size,
                                             block_index, self._config)

    def proxy_update_metadata(self, image_name, encoded_metadata):
        metadata_raw = json.loads(zlib.decompress(self._rpc_trans.decode(
                    encoded_metadata)))
        if image_name in self._metadata_dict:
            self._metadata_dict[image_name].metadata = metadata_raw
        else:
            metadata = UKAIMetadata(image_name, self._config, metadata_raw)
            self._metadata_dict[image_name] = metadata
            self._data_dict[image_name] = UKAIData(metadata,
                                                   self._node_error_state_set,
                                                   self._config)
            UKAIStatistics[image_name] = UKAIImageStatistics()

        return 0

    ''' Controll processing.
    '''
    def create_image(self, image_name, size, block_size=None,
                     location=None, hypervisor=None):
        assert image_name is not None
        assert size > 0

        if block_size is None:
            defaults = self._config.get('create_default')
            block_size = defaults['block_size']
        assert block_size > 0
        assert size > block_size
        assert size % block_size == 0
        block_count = size / block_size

        if location is None:
            location = self._config.get('core_server')
        if hypervisor is None:
            hypervisor = self._config.get('core_server')

        ukai_metadata_create(image_name, size, block_size,
                             location, hypervisor, self._config)

    def add_image(self, image_name):
        if image_name in self._metadata_dict:
            return errno.EEXIST
        metadata = UKAIMetadata(image_name, self._config)
        self._metadata_dict[image_name] = metadata
        data = UKAIData(metadata=metadata,
                        node_error_state_set=self._node_error_state_set,
                        config=self._config)
        self._data_dict[image_name] = data
        UKAIStatistics[image_name] = UKAIImageStatistics()
        return 0

    def remove_image(self, image_name):
        if image_name not in self._metadata_dict:
            return errno.ENOENT
        del self._metadata_dict[image_name]
        del self._data_dict[image_name]
        del UKAIStatistics[image_name]
        return 0

    def get_metadata(self, image_name):
        if image_name not in self._metadata_dict:
            return errno.ENOENT, None
        return 0, json.dumps(self._metadata_dict[image_name].metadata)

    def add_location(self, image_name, location,
                     start_index=0, end_index=-1,
                     sync_status=UKAI_OUT_OF_SYNC):
        if image_name not in self._metadata_dict:
            return errno.ENOENT
        metadata = self._metadata_dict[image_name]
        metadata.add_location(location, start_index, end_index, sync_status)
        return 0

    def remove_location(self, image_name, location,
                        start_index=0, end_index=-1):
        if image_name not in self._metadata_dict:
            return errno.ENOENT
        metadata = self._metadata_dict[image_name]
        metadata.remove_location(location, start_index, end_index)
        return 0 

    def add_hypervisor(self, image_name, hypervisor):
        if image_name not in self._metadata_dict:
            return errno.ENOENT
        metadata = self._metadata_dict[image_name]
        metadata.add_hypervisor(hypervisor)
        return 0

    def remove_hypervisor(self, image_name, hypervisor):
        if image_name not in self._metadata_dict:
            return errno.ENOENT
        metadata = self._metadata_dict[image_name]
        metadata.remove_hypervisor(hypervisor)
        return 0

    def synchronize(self, image_name, start_index=0, end_index=-1,
                    verbose=False):
        if image_name not in self._metadata_dict:
            return errno.ENOENT
        metadata = self._metadata_dict[image_name]
        data = self._data_dict[image_name]
        if end_index == -1:
            end_index = (metadata.size / metadata.block_size) - 1
        for block_index in range(start_index, end_index + 1):
            if verbose is True:
                print 'Syncing block %d (from %d to %d)' % (block_index,
                                                            start_index,
                                                            end_index)
            if data.synchronize_block(block_index) is True:
                metadata.flush()
        return 0

    def get_node_error_state_set(self):
        return self._node_error_state_set.get_list()
