import uuid
import simplejson
import threading
import logging
import time
import cPickle as pickle
import numpy as np

log = logging.getLogger(__name__)

"""
serialization functions for rpc server, we serialize json messages,
as well as python data, which are lists of numpy arrays.
msg serialization one object -> one string
data serialization list of arrays -> list of buffers/strings

we have 3 protocol levels here
1.  zeromq, functions exist to separate the envelope from the payload, and
pack those up as well.

2.  blaze protocol, blaze messages are the payloads of zeromq messages,
and are packaged into clientid, msgid, msgobj (json), dataobjects -
list data which can be serialized and deserialized

3.  rpc protocol, a layer around the msgobject and a data object
"""
serialize_json =  simplejson.dumps
deserialize_json = simplejson.loads

def default_serialize_data(data):
    """
    Parmeters
    ---------
    data : list of python objects (mostly numpy arrays)

    Returns
    ---------
    output : list of length 2n, where n is the number of objects.
        first item is pickled metadata, second is the data itself.
        for numpy arrays
        metadata : {'datatype' : 'numpy', 'dtype' : 'dtype', 'shape' : [2,2]}
        data : the array itself
        for arbitrary python objects
        metadata : {'datatype' : 'pickle'}
        data : pickled object
    """
    output = []
    for d in data:
        if isinstance(d, np.ndarray):
            metadata =  {'dtype' : d.dtype,
                         'shape' : d.shape,
                         'datatype' : 'numpy'}
            metadata = pickle.dumps(metadata)
            output.append(metadata)
            output.append(d)
        else:
            output.append(pickle.dumps({'datatype' : 'pickle'}))
            output.append(pickle.dumps(d))
    return output

def default_deserialize_data(input):
    """
    Parmeters
    ---------
    input : list of strings from default_serialize_data

    Returns
    ---------
    output : list of python objects, mostly numpy arrays
    """
    output = []
    curr_index = 0
    while curr_index < len(input):
        meta = pickle.loads(input[curr_index])
        if meta['datatype'] == 'numpy':
            array = np.frombuffer(input[curr_index + 1],
                                  dtype=meta['dtype'])
            array = array.reshape(meta['shape'])
            output.append(array)
        elif meta['datatype'] == 'pickle':
            obj = pickle.loads(input[curr_index + 1])
            output.append(obj)
        curr_index += 2
    return output

class ProtocolHelper(object):
    """
    collections of functions to assist in working with protocols
    """
    def __init__(self,
                 serialize_msg=serialize_json,
                 deserialize_msg=deserialize_json,
                 serialize_data=default_serialize_data,
                 deserialize_data=default_deserialize_data,
                 serialize_web=serialize_json,
                 deserialize_web=deserialize_json):

        self.serialize_msg = serialize_msg
        self.deserialize_msg = deserialize_msg
        self.serialize_data = serialize_data
        self.deserialize_data = deserialize_data
        self.serialize_web = serialize_web
        self.deserialize_web = deserialize_web

    def status_obj(self, status):
        return {'msgtype' : 'status',
                'status' : status}

    def error_obj(self, error_msg):
        return {
            'msgtype' : 'error',
            'error_msg' : error_msg}

    def working_obj(self, request_id):
        return {
            'msgtype' : 'rcpstatus',
            'status' : 'working',
            'request_id' : request_id}

    def unpack_rpc(self, responseobj, dataobj):
        """see package_rpc_response from BaseRPCServer
        """
        return responseobj['rpcresponse'], dataobj

    def pack_rpc(self, responseobj, dataobj):
        """our rpc functions return arbitrary json objects,
        and a list of numpy arrays.  this packages them up in the protocol.
        right now all we do is wrap the arbitrary responesobj in
        {'rpcresponse' : responseobj}, so we know where it came from
        """
        return {'msgtype' : 'rpcresponse',
                'rpcresponse' : responseobj}, dataobj

    def unpack_blaze(self, messages, deserialize_data=True):
        clientid = messages[0]
        messageid = messages[1]
        msgstr = messages[2]
        datastrs = messages[3:]
        msgobj = self.deserialize_msg(msgstr)
        if deserialize_data:
            return [clientid, messageid, msgobj, self.deserialize_data(datastrs)]
        else:
            return [clientid, messageid, msgobj, datastrs]

    def pack_blaze(self, client_id, message_id, msgobj, dataobjs,
                   serialize_data=True):
        msgstr = self.serialize_msg(msgobj)
        if serialize_data:
            datastrs = self.serialize_data(dataobjs)
        else:
            datastrs = dataobjs
        return [client_id, message_id, msgstr] + datastrs

    #handling zeromq req rep enveloping
    #these messages look like
    #[identity1, identy2, ..., '', content1, content2]
    #http://www.zeromq.org/tutorials:xreq-and-xrep

    def unpack_envelope(self, messages):
        try:
            nullindex = messages.index('')
            envelope = messages[:nullindex]
            payload = messages[nullindex+1:]
        except ValueError as e:
            envelope = [],
            payload = messages
        return envelope, payload

    def pack_envelope(self, envelope, payload):
        return envelope + [''] + payload

    def pack_envelope_blaze(self, envelope, clientid, msgid,
                            msgobj, dataobjs,
                            serialize_data=True):
        msg = self.pack_blaze(clientid, msgid, msgobj,
                              dataobjs, serialize_data=serialize_data)
        msg = self.pack_envelope(envelope, msg)
        return msg

    def unpack_envelope_blaze(self, messages, deserialize_data=True):
        envelope, messages = self.unpack_envelope(messages)
        (clientid,
         msgid,
         msgobj,
         dataobjs) = self.unpack_blaze(messages)
        return (envelope, clientid, msgid, msgobj, dataobjs)


