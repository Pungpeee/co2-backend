Vue.component('general-radio', {
  props: {
    label: { type: String, require: true },
    prop: { type: String, require: true },
    scope: { type: Object, require: true },
    options: { type: Array, require: true },
    isVertical: { type: Boolean, default: false }
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
    <general-input :label="label" :prop="prop" :scope="scope" class="general-radio" is-custom>
      <el-radio-group v-model="scope[prop]" :disabled="Boolean(colorClass)" @change="onChange">
        <el-radio v-for="(option, index) in options" :key="index" :label="option.label" :class="(isVertical ? 'block m-l-0 ' : 'inline-block ') + colorClass">
          {{ option.name }}
        </el-radio>
      </el-radio-group>
    </general-input>
  `
})