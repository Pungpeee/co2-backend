Vue.prototype.$eventHub = new Vue()

var feature = new Vue({
  el: '#feature',
  delimiters: [ '<%', '%>' ],
  store: vueStore,
  data () {
    return {
      name: 'theme',
      form: null,
      sortingItem: [],
      windowWidth: 0,
      colorClass: ''
    }
  },
  methods: {
    sortFeatures ({ feature, list }) {
      let status = 'pending'
      feature.class = status
      const data = { [feature.key]: list }
      this.$store.dispatch('createItem', { apiPath: 'setup/config/setup-sorting/', data }).then(res => status = 'success').catch(err => status = 'failed').finally(res => {
        setTimeout(() => {
          feature.class = status
          const message = 'Sorting: ' + feature.key + (status === 'success' ? ' has been saved.' : 'got an error')
          this.$message({ message, type: (status === 'success' ? 'success' : 'error'), duration: 1000 })
        }, 1000)
        setTimeout(() => { feature.class = '' }, 2000)
      })
    },
    onSubmit () {
      console.log('Submit')
      console.log(this.form)
    },
    onReset () {
      console.log('Reset')
    }
  },
  watch: {
    '$store.state.config' (val, oldVal) {
      if (val) {
        this.$store.dispatch('initFeatureForm').then(form => {
          this.form = form
        })
      }
    }
  }
})