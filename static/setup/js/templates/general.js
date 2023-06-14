new Vue({
  el: '#general',
  delimiters: [ '<%', '%>' ],
  store: vueStore,
  data () {
    return {
      name: 'general',
      form: null,
      langOption: [
        { label: '0', name: 'English' },
        { label: '1', name: 'Thai' }
      ],
      loginKeyOption: [
        { label: 'username_or_email', name: 'Username or Email' },
        { label: 'username', name: 'Username' },
        { label: 'email', name: 'Email' }
      ]
    }
  },
  methods: {
  },
  watch: {
    '$store.state.config' (val, oldVal) {
      if (val) {
        this.$store.dispatch('initGeneralForm', { versions }).then(form => {
          this.form = form
        })
      }
    }
  }
})