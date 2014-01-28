define [
  "jquery"
  "IPython"
], ($, IPython) ->

  init_kernel = (ws_url) ->
    kernel = new IPython.Kernel('/kernels')
    kernel._kernel_started({kernel_id: '1', ws_url: ws_url})
    kernel

  return {
    init_kernel: init_kernel
  }
