Vue.component('general-input', {
  props: {
    scope: { type: Object, require: true },
    prop: { type: String, require: true },
    label: { type: String, require: true },
    placeHolder: { type: String, default: '' },
    actionWidth: { type: Number, default: 200 },
    inputType: { type: String, default: 'text' },
    isCustom: { type: Boolean, default: false },
    hasAction: { type: Boolean, default: false },
    hasDetail: { type: Boolean, default: false }
  },
  computed: {
    actionStyle () {
      return 'width: ' + (this.hasAction ? 'calc(100% - ' + (this.actionWidth + 10) + 'px)' : '100%')
    }
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
    <el-form-item class="general-input" :label="label" :prop="prop">
      <div class="input inline-block vertical-top" :style="actionStyle">
        <slot v-if="isCustom"></slot>
        <el-input v-else :class="colorClass" :type="inputType" v-model="scope[prop]" :placeholder="placeHolder" autocomplete="off"
          :autosize="{ minRows: 3, maxRows: 6 }" :disabled="Boolean(colorClass)" @change="onChange"></el-input>
      </div>
      <div v-if="hasAction" class="action inline-block p-l-20" :style="'width: ' + actionWidth + 'px'">
        <slot name="action"></slot>
      </div>
      <div v-if="hasDetail" class="detail">
        <slot name="detail"></slot>
      </div>
    </el-form-item>
  `
})