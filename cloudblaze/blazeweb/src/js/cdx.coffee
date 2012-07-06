# CDX Coffee Script
#
# This is the main script file for the CDX app.

# module setup stuff
if this.cdx
  cdx = this.cdx
else
  cdx = {}
  this.cdx = cdx

# Menu functions
cdx.getDataListing  = (baseUrl) ->
    return

cdx.onShowModal = (modalId) ->
    $(modalId).children(".modal-body").append("<p>this is the body content</p>")
    return

