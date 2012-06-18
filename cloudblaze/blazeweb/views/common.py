from flask import (
	render_template, request, current_app,
	send_from_directory, make_response)
import simplejson

def get_slice(request):
    data_slice=request.args.get('data_slice', None)
    if data_slice is None:
        data_slice = [0, 100]
    else:
        data_slice = simplejson.loads(data_slice)
    return data_slice
    

