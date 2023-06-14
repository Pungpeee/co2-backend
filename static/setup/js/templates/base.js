Vue.use(Vuex)

const vueStore = new Vuex.Store({
  state: storeState,
  getters: storeGetters,
  mutations: storeMutations,
  actions: storeActions
})

let base = new Vue({
  el: '#base',
  delimiters: [ '<%', '%>' ],
  store: vueStore,
  created () {
    this.$store.dispatch('getProfile', {})
    this.$store.dispatch('getConfig', {}).then(res => {
      setTimeout(() => this.$store.commit('setState', { name: 'isLoading', val: false }), 250)
    })
  },
  data () {
    return {
      account: null,
      visible: false,
      leftMenuOpened: localStorage.getItem('setup-left-menu') === 'false' ? false : true,
      accountMenu: false
    }
  },
  mounted () {
    document.getElementById('body').style.opacity = '1'
    this.updateLeftMenu(this.leftMenuOpened, null)
    this.getWindowWidth()
    window.addEventListener('resize', this.getWindowWidth)
  },
  computed: {
    browseMenus () {
      return [
        {
          head: '',
          menus: [
            { name: 'General Setting', icon: 'settings', href: '/setup/' },
            { name: 'Theme Change', icon: 'color_lens', href: '/setup/theme-change' },
            // { name: 'Status Color', icon: 'format_paint', href: '/setup/status-color' },
            { name: 'Feature', icon: 'view_module', href: '/setup/feature' },
            // { name: 'Notification', icon: 'notifications', href: '/setup/notification' },
            // { name: 'Mail Template', icon: 'email', href: '/setup/mail-template' },
            { name: 'Export / Import', icon: 'import_export', href: '/setup/export-import' }
          ]
        }
      ]
    },
    activeMenu () {
      return this.browseMenus[0].menus.map(function (menu) { return menu.href }).indexOf(window.location.pathname)
    }
  },
  methods: {
    getWindowWidth () {
      this.$store.commit('setState', { name: 'onMobile', val: window.innerWidth <= 768 })
      this.$store.commit('setState', { name: 'windowWidth', val: window.innerWidth })
      this.leftMenuOpened = !this.$store.state.onMobile
    },
    updateLeftMenu (val, oldVal) {
      localStorage.setItem('setup-left-menu', val)
      if (val) $('#content').addClass('left-menu-opened')
      else $('#content').removeClass('left-menu-opened')
    }
  },
  watch: {
    leftMenuOpened (val, oldVal) {
      this.updateLeftMenu(val, oldVal)
    },
    '$store.state.isLoading' (val, oldVal) {
      if (val) document.getElementById('screen-loading').style.display = 'block'
      else document.getElementById('screen-loading').style.display = 'none'
    }
  }
})
