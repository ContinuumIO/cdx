import urlparse
1/0
def get_summary(client, datapath):
    if not datapath.startswith("/"):
        datapath = "/" + datapath
    summary, _ = client.rpc(
        'summary', datapath)
    return summary

def get_tree(client, datapath, depth=None):
    if not datapath.startswith("/"):
        datapath = "/" + datapath
    tree, _ = client.rpc(
        'get_metadata_tree', datapath,
        depth=depth)
    return tree


def raw_get(client, datapath, data_slice=None):
    if not datapath.startswith("/"):
        datapath = "/" + datapath
    retval, dataobj = client.rpc(
        'get', datapath,
        data_slice=data_slice)
    return retval, dataobj

def build_table(array, shape, data_slice, datapath, columns=None):
    if len(array.shape) < 2:
        array = [[x] for x in array]
        if columns is None:
            columns = range(1)
    else:
        columns = range(array.shape[1])
        if columns is None:
            columns = range(array.shape[1])
        array = array.tolist()
    return dict(columns=columns,
                data=array,
                data_slice=data_slice,
                total_rows=shape[0],
                url=urlparse.urljoin("/data/", datapath))
