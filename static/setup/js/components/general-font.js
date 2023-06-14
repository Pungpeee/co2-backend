Vue.component('general-font', {
  props: {
    label: { type: String, require: true },
    prop: { type: String, require: true },
    scope: { type: Object, require: true },
    options: { type: Array, require: true },
    actionWidth: { type: Number, default: 150 }
  },
  computed: {
    actionStyle () {
      return 'width: calc(100% - ' + (this.actionWidth + 50 + 15 ) + 'px)'
    }
  },
  template: `
    <general-input :label="label" :prop="prop" :scope="scope" class="general-font" is-custom>
      <div v-for="(font, index) in scope[prop]" :key="index" class="block p-b-10">
        <div class="font-type text-right inline-block vertical-top" style="width: 50px">{{ font.type }}</div>
        <div class="font-file text-grey inline-block p-l-20" :style="actionStyle">{{ font.file && font.file.name ? font.file.name : 'font' + font.type }}</div>
        <div class="upload-area inline-block text-right vertical-top p-l-20" :style="'width: ' + actionWidth + 'px'">
          <div class="upload-btn-wrapper">
            <el-button class="btn-inline btn-main-color "><input type="file" title=" " @change="function(e){ scope[prop][index].file = e.target.files[0] }" />Upload Font</el-button>
          </div>
        </div>
      </div>
    </general-input>
  `
})