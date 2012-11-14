$CDX.ws_conn_string = "wss://#{window.location.host}/cdx/sub"
$(()->
  $CDX.utility.load_default_document()
)
