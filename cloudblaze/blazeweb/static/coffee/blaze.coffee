$CDX.blaze = {}
$CDX.blaze.get_summary = (variables, callback) ->
  toquery = []
  for namespaceobj in variables
    if namespaceobj.type == 'BlazeArrayProxy'
      toquery.push(_.clone(namespaceobj))
  urls = (x.url for x in toquery)
  wrapped_callback = (data) ->
    wrapped = _.zip(toquery, data)
    callback(wrapped)
  ajaxopts =
    type : 'GET'
    url : '/bulksummary'
    data : {paths : JSON.stringify(urls)}
    contentType:"application/json; charset=utf-8"
    dataType:"json"
    success : wrapped_callback

  $.ajax(ajaxopts)

$CDX.blaze.set_data_source = (url, data_source) ->
  deferred = $.get("/data" + url, {}, (data) ->
    arraydata = JSON.parse(data)
    transformed = []
    for row in arraydata['data']
      transformedrow = {}
      for temp in _.zip(row, arraydata['colnames'])
        [val, colname] = temp
        transformedrow[colname] = val
      transformed.push(transformedrow)
    data_source.set('data', transformed)
  )
