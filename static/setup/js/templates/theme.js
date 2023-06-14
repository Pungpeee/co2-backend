new Vue({
  el: '#theme',
  delimiters: [ '<%', '%>' ],
  store: vueStore,
  data () {
    return {
      name: 'theme',
      form: null,
      originalForm: null
    }
  },
  methods: {
  },
  watch: {
    '$store.state.config' (val, oldVal) {
      if (val) {
        this.$store.dispatch('initThemeForm').then(form => {
          this.form = form
        })
      }
    }
  }
})