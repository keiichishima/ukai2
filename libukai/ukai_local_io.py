import os

def ukai_local_read(image_name, block_size, block_index, offset, size, config):
    path = '%s/%s/' % (config.get('data_root'), image_name)
    path = path + config.get('blockname_format') % block_index
    fh = open(path, 'r')
    fh.seek(offset)
    data = fh.read(size)
    fh.close()
    assert data is not None

    return data

def ukai_local_write(image_name, block_size, block_index, offset, data, config):
    path = '%s/%s/' % (config.get('data_root'), image_name)
    path = path + config.get('blockname_format') % block_index
    if not os.path.exists(path):
        # XXX shoud not happen.
        return 0
    fh = open(path, 'r+')
    fh.seek(offset)
    fh.write(data)
    fh.close()

    return len(data)

def ukai_local_allocate_dataspace(image_name, block_size, block_index, config):
    path = '%s/%s/' % (config.get('data_root'), image_name)
    if not os.path.exists(path):
        os.makedirs(path)
    path = path + config.get('blockname_format') % block_index
    fh = open(path, 'w')
    fh.seek(block_size - 1)
    fh.write('\0')
    fh.close()

    return 0
