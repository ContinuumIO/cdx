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
cdx.getDataListing = (baseUrl) ->
    return

cdx.addDataArray = (url) ->
    alert('data array selected: ' + url)
    return

cdx.addDataArrayTab = (url) ->
    alert('data array selected: ' + url)
    data_slice = JSON.stringify([0, 100])
    url = '/dataview' + url + '?data_slice=' + data_slice
    alert('data url: ' + url)
    $.get(url, {}, (data) ->
#        treeData = $.parseJSON(data)
        console.log(data)
    )
    return

cdx.showModal = (modalID) ->
    $(modalID).empty()
    $.get('/metadata/blaze/data/gold.hdf5?depth=2', {}, (data) ->
        treeData = $.parseJSON(data)
        #console.log(JSON.stringify('treeData.url='+treeData.url)+'\n##')
        #console.log(JSON.stringify('treeData.type='+treeData.type)+'\n##')
        treeRoot = '<div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal">×</button>
                        <h3>Select A Data Set</h3>
                    </div>
                   <div class="modal-body">
                        <div class="css-treeview">
                        <ul>
                            <li><input type="checkbox" checked="checked" id="root-0" />
                            <label for="root-0">Data Tree</label>\n<ul>'
        #console.log(treeRoot)
        tree = cdx.buildTreeNode(treeRoot, treeData.children, 0)
        tree = tree + '</ul></li></ul></div></div>'
        $(modalID).append(tree)
        $(modalID).modal('show')
        #console.log(tree)
    )
    return

cdx.buildTreeNode = (tree, treeData, depth) ->
    #console.log(JSON.stringify(treeData));
    loopCount = 0
    $.each(treeData, () ->
        loopCount++
        urlStr = JSON.stringify(this.url)
        #console.log('##\nurl='+urlStr+'\n')
        #console.log('type='+JSON.stringify(this.type)+'\n##')
        itemName = this.url.split('/').reverse()[0]
        if (this.type == 'group')
            itemID = 'item-' + depth
            `
            for(i=0; i<depth; i++) {
                itemID = itemID + '-' + i
            }
            tmp = '<li><input type="checkbox" id="' + itemID + 
                '" /><label for="' + itemID +'">' + itemName +
                '</label>\n<ul>'
            `
            tree = tree + tmp
            tree = cdx.buildTreeNode(tree, this.children, ++depth)
            tree = tree + '\n</ul></li>'
        if (this.type == 'array')
            #console.log('array type'+JSON.stringify(this.type)+'\n##')
            tmp = "<li><a href=\"#\" onClick=\"cdx.addDataArrayTab('" + this.url + "')\">" + itemName + "</a></li>"
            tree = tree + tmp
    ) if treeData
    return tree
    
cdx.showDataImportModal = (modalID) ->
    $(modalID).empty()
    tree = '<div class="modal-header">
            <button type="button" class="close" data-dismiss="modal">×</button>
            <h3>Import a Local Data File</h3>
            </div>
            <div class="modal-body">'
    #console.log(treeRoot)
    tree = tree + '</div>'
    $(modalID).append(tree)
    $(modalID).modal('show')
    return


