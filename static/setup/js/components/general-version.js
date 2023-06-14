Vue.component('general-version', {
  props: {
    label: { type: String, require: true },
    prop: { type: String, require: true },
    scope: { type: Object, require: true }
  },
  template: `
    <general-input :label="label" :prop="prop" :scope="scope" class="general-version p-t-5 p-b-5" is-custom has-action>
      <div class="text-right" slot="action">
        <span class="text-grey font-14">{{ scope[prop] !== 'None' && scope[prop] || 'No version log' }}</span>
      </div>
    </general-input>
  `
})