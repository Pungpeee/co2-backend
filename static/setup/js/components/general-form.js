Vue.component('general-form', {
  props: {
    form: { type: Object, require: true },
    rules: { type: Object, default: {} },
    nameWidth: { type: Number, default: 240 },
    relativeFooter: { type: Boolean, default: false }
  },
  methods: {
    submit () {
      this.$emit('submit')
    }
  },
  template: `
    <div class="general-form">
      <el-form :model="form" :rules="rules" ref="generalForm" :label-width="nameWidth + 'px'">
        <slot :form="form"></slot>
      </el-form>
      <div v-if="false" :class="relativeFooter ? 'relative-footer' : 'footer'">
        <el-button class="btn-inline btn-main-color-outline pointer" @click="$emit('reset')">Reset to Default</el-button>
        <el-button class="btn-inline btn-main-color pointer" @click="submit">Apply</el-button>
      </div>
    </div>
  `
})