Vue.component('general-upload', {
  props: {
    label: { type: String, require: true },
    prop: { type: String, require: true },
    scope: { type: Object, require: true },
    buttonLabel: { type: String, default: 'Upload Image' },
    example: { type: String, default: 'image.png' },
    specific: { type: String, default: '' },
    buttonWidth: { type: Number, default: 150 },
    hideContent: { type: Boolean, default: false },
    isImage: { type: Boolean, default: true },
    customApi: { type: Boolean, default: false },
    accept: { type: String, default: 'image/*' }
  },
  data () {
    return {
      colorClass: '',
      file: null,
      previewImage: this.isImage ? this.scope[this.prop] && this.scope[this.prop].value : ''
    }
  },
  methods: {
    changeInputStatus (status) {
      setTimeout(() => {
        this.colorClass = status
        const message = this.scope[this.prop].key + (status === 'success' ? ' has been saved.' : 'got an error')
        this.$message({ message, type: (status === 'success' ? 'success' : 'error'), duration: 1000 })
      }, 1000)
      setTimeout(() => { this.colorClass = '' }, 2000)
    },
    uploadFile (e) {
      let status = 'pending'
      this.colorClass = status
      const setPreview = (file, key) => {
        this.scope[this.prop] = ({
          name: file.name,
          key: key || this.scope[this.prop].key,
          file: file
        })
      }
      if (this.isImage) {
        setPreview(e.target.files[0])
        var reader = new FileReader()
        reader.onload = e => {
          this.previewImage = e.target.result
          this.$store.dispatch('editItem', { apiPath: 'setup/config/' + this.scope[this.prop].key + '/', data: { image: e.target.result } })
          .then(res => status = 'success')
          .catch(err => status = 'failed')
          .finally(res => this.changeInputStatus(status))
        }
        reader.readAsDataURL(e.target.files[0])
      } else {
        setPreview(e.target.files[0], 'import ' + e.target.files[0].name)
        let formData = new FormData()
        formData.append('file', e.target.files[0])
        this.$store.dispatch('createItem', { apiPath: 'setup/config/import/', data: formData, header: { 'Content-Type': 'multipart/form-data' } })
        .then(res => status = 'success')
        .catch(err => status = 'failed')
        .finally(res => this.changeInputStatus(status))
      }
    }
  },
  template: `
    <general-input :label="label" :prop="prop" :scope="scope" :actionWidth="buttonWidth" :class="'general-upload ' + (specific ? 'p-b-0' : '')" is-custom has-action :has-detail="specific !== ''">
      <el-popover v-if="isImage && scope[prop]" ref="preview" placement="top" width="250" trigger="hover">
        <img class="general-upload-img" :src="previewImage"/>
      </el-popover>
      <span v-if="scope[prop] && !hideContent" v-popover:preview :class="'upload-name ' + colorClass" :style="{ cursor: (isImage ? 'default' : 'auto') }">
        <div class="inline-block">{{ scope[prop].name || example }}</div>
      </span>
      <div v-if="!hideContent" class="text-right" slot="action">
        <div class="upload-btn-wrapper">
          <input ref="input-upload" class="pointer" type="file" title=" " :accept="accept" @change="e => customApi ? $emit('upload', e) : uploadFile(e)" />
          <el-button class="btn-inline btn-main-color" :disabled="Boolean(colorClass)" @click="$refs['input-upload'].click()">{{ buttonLabel }}</el-button>
        </div>
      </div>
      <div slot="detail" v-if="specific && !hideContent">
        <small class="specific text-grey">{{ specific }}</small>
      </div>
    </general-input>
  `
})