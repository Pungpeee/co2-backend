Vue.component('general-color-picker', {
  props: {
    label: { type: String, require: true },
    prop: { type: String, require: true },
    scope: { type: Object, require: true },
    status: { type: String, default: 'standby' },
    isDisabled: { type: Boolean, default: false },
    hasAction: { type: Boolean, default: false }
  },
  data () {
    return {
      colorClass: ''
    }
  },
  methods: {
    onChange (e) {
      let status = 'pending'
      this.colorClass = status
      this.$store.dispatch('editItem', { apiPath: 'setup/config/' + this.scope.key + '/', data: { value: this.scope[this.prop] } }).then(res => status = 'success').catch(err => status = 'failed').finally(res => {
        setTimeout(() => {
          this.colorClass = status
          const message = this.scope.key + (status === 'success' ? ' has been saved.' : 'got an error')
          this.$message({ message, type: (status === 'success' ? 'success' : 'error'), duration: 1000 })
        }, 1000)
        setTimeout(() => { this.colorClass = '' }, 2000)
      })
    }
  },
  template: `
  <general-input :label="label" :prop="prop" :scope="scope" class="general-color-picker" is-custom :has-action="hasAction">
    <span class="m-r-10">HEX</span>
    <div :class="'color-picker ' + colorClass">
      <input type="text" v-model="scope[prop]" :disabled="Boolean(colorClass) || isDisabled" class="input-color" placeholder="Hex color (#FFFFFF)"
        maxlength="7" spellcheck="false" @change="onChange">
      <el-color-picker v-model="scope[prop]" size="medium" :disabled="Boolean(colorClass) || isDisabled" @change="onChange"></el-color-picker>
    </div>
  </general-input>
  `
})