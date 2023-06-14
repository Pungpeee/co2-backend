Vue.component('feature-switch-group', {
  props: {
    features: { type: Array, require: true },
    type: { type: String, default: '' }
  },
  data () {
    return {
      val: false
    }
  },
  mounted () {
    this.$nextTick(() => {
      this.features.forEach((feature, i) => {
        if (feature.value) $('#subFeature' + i).collapse('show')
      })
    })
  },
  methods: {
    onMainFeatureChange (value, index) {
      this.features[index].other = this.features[index].other.map(feat => ({ ...feat, value }))
      this.features[index].value = value
      $('#subFeature' + index).collapse(value ? 'show' : 'hide')
      this.onChange(index)
    },
    onSubChange (val, index, indexSub) {
      this.features[index].other[indexSub].value = val
      this.onChange(index)
    },
    onChange (index) {
      const data = { feature: { [this.features[index].key]: { value: this.features[index].value, other: this.features[index].other } } }
      let status = 'pending'
      this.features[index].class = status
      this.$store.dispatch('createItem', { apiPath: 'setup/config/setup-update/', data }).then(res => status = 'success').catch(err => status = 'failed').finally(res => {
        setTimeout(() => {
          this.features[index].class = status
          const message = 'Feature: ' + this.features[index].key + (status === 'success' ? ' has been saved.' : 'got an error')
          this.$message({ message, type: (status === 'success' ? 'success' : 'error'), duration: 1000 })
        }, 1000)
        setTimeout(() => { this.features[index].class = '' }, 2000)
      })
    }
  },
  template: `
    <div class="feature-switch-group">
      <div class="features">
        <div v-for="(feature, i) in features" :key="feature.name" class="feature">
          <div :class="'main-feature ' + features[i].class">
            <general-switch class="flex" :label="feature.name" :value="feature.value" :disabled="Boolean(features[i].class)" @change="val => onMainFeatureChange(val, i)">
              <div v-if="feature.other.length > 0" class="name font-bold">{{ feature.name }} ({{ feature.other.length }})</div>
            </general-switch>
          </div>
          <div class="collapse sub-feature" :id="'subFeature' + i">
            <div :class="features[i].class">
              <general-switch v-for="(subFeature, j) in feature.other" :key="subFeature.name" class="flex" :label="subFeature.name" :disabled="Boolean(features[i].class)"
                :value="subFeature.value" @change="val => onSubChange(val, i, j)"/>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})