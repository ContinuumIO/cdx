from cdx.app import app
from flask import (
    render_template, request, current_app,
    send_from_directory, make_response)
import flask
import os
import logging
import uuid
import urlparse
import cdx.arrayserverclient as arrayserverclient
import cdx.views.common as common
import cdx.bbmodel as bbmodel
import cdx.wsmanager as wsmanager
import pandas

log = logging.getLogger(__name__)
1/0

@app.route("/summary/<path:datapath>")
def summary(datapath):
    summary =  arrayserverclient.get_summary(current_app.rpcclient, datapath)
    return current_app.ph.serialize_web(summary)

@app.route("/bulksummary/")
def bulk_summary():
    paths = app.ph.deserialize_web(request.args['paths'])
    summaries = []
    for p in paths:
        try:
            summary = arrayserverclient.get_summary(current_app.rpcclient, p)
        except Exception as e:
            log.exception(e)
            summary = None
        summaries.append(summary)
    print 'SUMMARIES', summaries
    return current_app.ph.serialize_web(summaries)
