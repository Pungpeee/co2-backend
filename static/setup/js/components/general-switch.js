Vue.component('general-switch', {
  props: {
    label: { type: String, require: true },
    value: { type: Boolean, require: true },
    width: { type: Number, default: 70 },
    disabled: { type: Boolean, default: false }
  },
  data () {
    return {
      switchHeight: ''
    }
  },
  template: `
    <div class="general-switch">
      <slot><div class="name">{{ label }}</div></slot>
      <el-switch class="switch" v-model="value" :width="width" :disabled="disabled" @change="val => $emit('change', val)"></el-switch>
    </div>
  `
})