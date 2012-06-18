from cloudblaze.blazeweb.app import app
from flask import (
	render_template, request, current_app,
	send_from_directory, make_response, session)

@app.route('/authtest', methods=['GET'])
def test():
    print 'authtest', session
    return session.get('username', 'WRONG')
