$CDX.blaze = {}
$CDX.blaze.get_summary = (variables, options) ->
  toquery = []
  for namespaceobj in variables
    if namespaceobj.type == 'BlazeArrayProxy'
      toquery.push(_.clone(namespaceobj))
  urls = (x.url for x in toquery)
  ajaxopts =
    type : 'GET'
    url : '/bulksummary'
    data : {paths : JSON.stringify(urls)}
    contentType:"application/json; charset=utf-8"
    dataType:"json"
  _.extend(ajaxopts, options)
  $.ajax(ajaxopts)
