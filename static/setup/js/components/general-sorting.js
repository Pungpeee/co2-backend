Vue.component('general-sorting', {
  props: {
    list: { type: Object, require: true },
    prop: { type: String, default: 'is_display' },
    name: { type: String, default: 'code' },
    sort: { type: String, default: 'sort' },
    hasSwitch: { type: Boolean, default: false },
    type:  { type: String, require: false },
    disabled: { type: String, default: false }
  },
  data () {
    return {
      sortable: null,
      scrollingHeight: 0,
      form: Object.assign([], this.list)
    }
  },
  mounted () {
    this.$nextTick(() => {
      this.sortable = Sortable.create(this.$refs.generalSorting, {
        animation: 300,
        onUpdate: this.updateItem
      })
    })
  },
  methods: {
    toggleItem (item, val) {
      item[this.prop] = val
      this.form.find(f => f.id === item.id)[this.prop] = val
      this.$emit('sorted', this.form)
    },
    updateItem (e) {
      const dragUp = e.newIndex < e.oldIndex
      const newIndex = dragUp ? e.newIndex : e.newIndex + 1
      const oldIndex = dragUp ? e.oldIndex + 1 : e.oldIndex
      this.form.splice(newIndex, 0, this.form[e.oldIndex])
      this.form.splice(oldIndex, 1)
      this.form = this.form.map((item, index) => ({ ...item, sort: index + 1 }))
      this.$emit('sorted', this.form)
    }
  },
  watch: {
    'disabled' (val, oldVal) {
      this.sortable.option('disabled', val)
    }
  },
  template: `
    <div class="general-sorting" ref="generalSorting">
      <div v-for="item in list" :key="item[name]" :class="'item ' + (item[prop] ? '' : 'off')" draggable="true">
        <div class="item-icon">
          <i class="material-icons">drag_handle</i>
        </div>
        <div class="item-info">
          <general-switch v-if="hasSwitch" class="flex" :label="item[name]" :value="item[prop]" :disabled="disabled" @change="val => toggleItem(item, val)"></general-switch>
          <div v-else class="name">{{ item[name] }}</div>
        </div>
      </div>
    </div>
  `
})