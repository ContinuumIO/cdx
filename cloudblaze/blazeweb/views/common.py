from flask import (
	render_template, request, current_app,
	send_from_directory, make_response)

def get_slice(request):
    data_slice=request.args.get('data_slice', None)
    if data_slice is None:
        data_slice = [0, 100]
    else:
        data_slice = current_app.ph.deserialize_web(data_slice)
    return data_slice
    

