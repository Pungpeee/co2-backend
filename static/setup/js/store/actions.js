const storeActions = {
  async axiosRequest ({ state, dispatch }, { method = 'get', apiPath, data = {}, query = {}, header = {} }) {
    apiPath = await dispatch('getApiPath', { apiPath, query })
    return new Promise ((resolve, reject) => {
      headers = { ...header, 'X-CSRFToken': document.cookie.split(';').find(cookie => cookie.includes('csrftoken')).split('=').pop() }
      state.requests.push({ apiPath, method, data, query, header, status: null })
      const index = state.requests.length - 1
      axios({ headers, method, url: apiPath, data, responseType: 'json'}).then(res => {
        state.requests[index].status = 200
        resolve(res)
      }).catch(err => {
        state.requests[index].status = err.response.status
        if (err.response.status === 401) dispatch('getItem', { apiPath: 'account/profile/', query })        
        reject(err)
      })
    })
  },
  createItem ({ dispatch }, { apiPath, data, query = {}, header = {} }) {
    return dispatch('axiosRequest', { method: 'post', apiPath, data, query, header })
  },
  editItem ({ dispatch }, { apiPath, data, query = {}, header = {} }) {
    return dispatch('axiosRequest', { method: 'patch', apiPath, data, query, header })
  },
  getApiPath({}, { apiPath, query = {} }) {
    Object.assign(query, { format: 'json' })
    return '/api/' + apiPath + Object.keys(query).reduce((api, key) => api + (api.length > 1 ? '&' : '') + key + '=' + query[key], '?')
  },
  getItem ({ dispatch }, { apiPath, query = {}, header = {} }) {
    return dispatch('axiosRequest', { method: 'get', apiPath, query, header })
  },
  getConfig ({ state, dispatch }, { query = {} }) {
    return new Promise ((resolve, reject) => {
      dispatch('getItem', { apiPath: 'setup/config/', query }).then(res => {
        state.config = res.data
        resolve(res.data)
      }).catch(err => reject(err))
    })
  },
  getProfile ({ state, dispatch }, { query = {} }) {
    return new Promise ((resolve, reject) => {
      dispatch('getItem', { apiPath: 'account/profile/', query }).then(res => {
        state.account = res.data
        resolve(res.data)
      }).catch(err => {
        if (err.response.status < 500) location.href = '/admin/login/?next=' + window.location.pathname
        reject(err)
      })
    })
  },
  initGeneralForm ({ state }, { versions }) {
    const config = state.config.config_dict
    const getVal = key => ({ ...config[key], key })
    const getName = name => name.split('/').pop()
    return {
      name: getVal('config-app-name'),
      logo: { ...getVal('config-logo'), name: getName(config['config-logo'].value) },
      footerLogo: null,
      favicon: { ...getVal('config-favicon'), name: getName(config['config-favicon'].value) },
      language: getVal('config-default-language'),
      loginKey: getVal('account-login-key'),
      fonts: [
        { type: '.ttf', file: null },
        { type: '.eot', file: null },
        { type: '.svg', file: null },
        { type: '.woff', file: null },
        { type: '.woff2', file: null },
      ],
      analyticsKey: getVal('config-google-analytics'),
      versions
    }
  },
  initExportImportForm (form) {
    return {
      export: { name: 'export' },
      import: { name: ' ' }
    }
  },
  initThemeForm ({ state}, form) {
    const config = state.config.config_dict
    const getVal = key => ({ ...config[key], key })
    const getName = name => name.split('/').pop()
    return {
      theme: {
        primaryColor: getVal('config-primary-color'),
        secondaryColor: getVal('config-secondary-color'),
      },
      login: {
        logo:  { ...getVal('config-login-logo'), name: getName(config['config-login-logo'].value) },
        background:  { ...getVal('config-login-background'), name: getName(config['config-login-background'].value) },
        textColor: getVal('config-login-text-color'),
        buttonColor: getVal('config-login-button-color'),
        buttonTextColor: getVal('config-login-button-text-color'),
        titleText: getVal('config-login-title'),
        footerText: getVal('config-login-footer')
      },
      header: {
        background: getVal('config-header-background-color'),
        textColor: getVal('config-header-text-color'),
        iconColor: ''
      },
      menu: {
        showMenu: true,
        background: getVal('config-menu-background-color'),
        textColor: getVal('config-menu-text-color'),
        selectedTextColor: getVal('config-menu-text-selected-color'),
        iconColor: getVal('config-menu-icon-color'),
        selectedIconColor: getVal('config-menu-icon-selected-color'),
        indicator: getVal('config-menu-indicator-color')
      },
      body: {
        background: getVal('config-background-color'),
        headerColor: getVal('config-heading-color'),
        titleColor: getVal('config-title-color'),
        descriptionColor: getVal('config-description-color'),
        informationColor: getVal('config-information-color'),
        category: {
          display: true,
          image: ''
        },
        contentProvider: {
          display: true,
          image: ''
        },
        instructor: {
          display: true,
          image: ''
        }
      }
    }
  },
  initFeatureForm ({ state }, form) {
    const features = state.config.feature
    const getVal = key => ({ ...features[key], key })
    return {
      features: [
        { name: 'Course', class: '', ...getVal('course') },
        { name: 'Test', class: '', ...getVal('exam') }
      ],
      sortingFeatures: [
        { name: 'Home - Web', key: 'home', class: '', list: state.config.home.filter(home => home.device === 1) },
        { name: 'Side Menu - Web', key: 'side_menu', class: '', list: state.config.side_menu.sort((curr, next) => curr.sort - next.sort) },
        { name: 'Home - Mobile', key: 'home', class: '', list: state.config.home.filter(home => home.device === 2) }
      ]
    }
  },
  logout ({ state, commit, dispatch }, { query = {} }) {
    return new Promise ((resolve, reject) => {
      dispatch('getItem', { apiPath: 'account/logout/', query }).then(res => {
        state.account = null
        location.href = '/admin/login/?next=/setup/'
        resolve(res.data)
      }).catch(err => reject(err))
    })    
  }
}
