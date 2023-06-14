const storeGetters = {
  getInputStatus (state) {
    return ['patch', 'post'].includes(state.requestType) && state.requestStatus || ''
  }
}