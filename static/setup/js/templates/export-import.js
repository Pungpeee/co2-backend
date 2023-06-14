new Vue({
  el: '#export-import',
  delimiters: [ '<%', '%>' ],
  store: vueStore,
  data () {
    return {
      form: null,
      text: ''
    }
  },
  watch: {
    '$store.state.config' (val, oldVal) {
      if (val) {
        this.$store.dispatch('initExportImportForm').then(form => {
          this.form = form
        })
      }
    }
  }
})