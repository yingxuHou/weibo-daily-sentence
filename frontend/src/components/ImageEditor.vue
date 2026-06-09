<template>
  <div class="image-editor">
    <div class="editor-header">
      <h3>图片编辑器</h3>
      <div class="editor-actions">
        <button class="btn-icon" @click="generateImage" :disabled="generating" title="生成背景图">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
          </svg>
        </button>
        <button class="btn-icon" @click="addText" title="添加文字">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="4 7 4 4 20 4 20 7"/>
            <line x1="9" y1="20" x2="15" y2="20"/>
            <line x1="12" y1="4" x2="12" y2="20"/>
          </svg>
        </button>
        <button class="btn-icon" @click="addLogo" title="添加Logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
            <line x1="12" y1="22.08" x2="12" y2="12"/>
          </svg>
        </button>
        <button class="btn-icon" @click="deleteSelected" title="删除选中">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        </button>
        <button class="btn primary" @click="exportImage" :disabled="exporting">
          {{ exporting ? '导出中...' : '导出图片' }}
        </button>
      </div>
    </div>

    <div class="editor-body">
      <!-- Canvas 画布 -->
      <div class="canvas-container">
        <canvas ref="canvasRef" id="fabricCanvas"></canvas>
        <div v-if="generating" class="loading-overlay">
          <div class="spinner"></div>
          <p>AI 正在生成图片... (30-60秒)</p>
        </div>
      </div>

      <!-- 右侧属性面板 -->
      <div class="properties-panel">
        <div v-if="!selectedObject" class="empty-state">
          <p>选择图层查看属性</p>
        </div>

        <!-- 文字属性 -->
        <div v-if="selectedObject && selectedObject.type === 'text'" class="property-group">
          <h4>文字属性</h4>

          <div class="property-field">
            <label>内容</label>
            <textarea v-model="textContent" @input="updateText" rows="3"></textarea>
          </div>

          <div class="property-row">
            <div class="property-field">
              <label>字号</label>
              <input type="number" v-model.number="fontSize" @input="updateFontSize" min="12" max="120">
            </div>
            <div class="property-field">
              <label>行高</label>
              <input type="number" v-model.number="lineHeight" @input="updateLineHeight" min="1" max="3" step="0.1">
            </div>
          </div>

          <div class="property-field">
            <label>字体</label>
            <select v-model="fontFamily" @change="updateFontFamily">
              <option value="'PingFang SC', sans-serif">苹方</option>
              <option value="'Microsoft YaHei', sans-serif">微软雅黑</option>
              <option value="'Noto Sans SC', sans-serif">思源黑体</option>
              <option value="'STKaiti', serif">楷体</option>
              <option value="'STSong', serif">宋体</option>
            </select>
          </div>

          <div class="property-field">
            <label>颜色</label>
            <div class="color-picker">
              <input type="color" v-model="textColor" @input="updateTextColor">
              <input type="text" v-model="textColor" @input="updateTextColor" class="color-input">
            </div>
          </div>

          <div class="property-row">
            <label class="checkbox-label">
              <input type="checkbox" v-model="textBold" @change="updateTextStyle">
              <span>粗体</span>
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="textItalic" @change="updateTextStyle">
              <span>斜体</span>
            </label>
          </div>

          <div class="property-field">
            <label>对齐</label>
            <div class="align-buttons">
              <button @click="updateTextAlign('left')" :class="{active: textAlign === 'left'}">左对齐</button>
              <button @click="updateTextAlign('center')" :class="{active: textAlign === 'center'}">居中</button>
              <button @click="updateTextAlign('right')" :class="{active: textAlign === 'right'}">右对齐</button>
            </div>
          </div>

          <!-- 艺术字效果 -->
          <div class="property-group">
            <h4>艺术字效果</h4>

            <div class="property-field">
              <label>描边颜色</label>
              <div class="color-picker">
                <input type="color" v-model="strokeColor" @input="updateStroke">
                <input type="text" v-model="strokeColor" @input="updateStroke" class="color-input">
              </div>
            </div>

            <div class="property-field">
              <label>描边宽度</label>
              <input type="range" v-model.number="strokeWidth" @input="updateStroke" min="0" max="10" step="1">
              <span>{{ strokeWidth }}px</span>
            </div>

            <div class="property-field">
              <label>阴影模糊</label>
              <input type="range" v-model.number="shadowBlur" @input="updateShadow" min="0" max="30" step="1">
              <span>{{ shadowBlur }}px</span>
            </div>

            <div class="property-row">
              <div class="property-field">
                <label>阴影 X</label>
                <input type="number" v-model.number="shadowX" @input="updateShadow" min="-20" max="20">
              </div>
              <div class="property-field">
                <label>阴影 Y</label>
                <input type="number" v-model.number="shadowY" @input="updateShadow" min="-20" max="20">
              </div>
            </div>

            <div class="property-field">
              <label>阴影颜色</label>
              <div class="color-picker">
                <input type="color" v-model="shadowColor" @input="updateShadow">
                <input type="text" v-model="shadowColor" @input="updateShadow" class="color-input">
              </div>
            </div>
          </div>
        </div>

        <!-- Logo 属性 -->
        <div v-if="selectedObject && selectedObject.type === 'image'" class="property-group">
          <h4>Logo 属性</h4>

          <div class="property-field">
            <label>版本</label>
            <select v-model="logoVersion" @change="changeLogo">
              <option value="color">原色</option>
              <option value="white">反白</option>
              <option value="black">墨稿</option>
            </select>
          </div>

          <div class="property-row">
            <div class="property-field">
              <label>宽度</label>
              <input type="number" v-model.number="logoWidth" @input="updateLogoSize" min="20" max="400">
            </div>
            <div class="property-field">
              <label>透明度</label>
              <input type="number" v-model.number="logoOpacity" @input="updateLogoOpacity" min="0" max="100" step="5">
            </div>
          </div>
        </div>

        <!-- 背景图属性 -->
        <div v-if="selectedObject && selectedObject.id === 'background'" class="property-group">
          <h4>背景图属性</h4>

          <div class="property-field">
            <label>不透明度</label>
            <input type="range" v-model.number="bgOpacity" @input="updateBgOpacity" min="0" max="100">
            <span>{{ bgOpacity }}%</span>
          </div>

          <button class="btn" @click="generateImage">重新生成背景</button>
        </div>

        <!-- 图层列表 -->
        <div class="layers-panel">
          <h4>图层</h4>
          <div class="layer-list">
            <div
              v-for="obj in canvasObjects"
              :key="obj.id"
              class="layer-item"
              :class="{active: selectedObject && selectedObject.id === obj.id}"
              @click="selectLayer(obj)"
            >
              <span class="layer-icon">
                <svg v-if="obj.type === 'text'" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M5 4v3h5.5v12h3V7H19V4z"/>
                </svg>
                <svg v-else-if="obj.type === 'image'" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                </svg>
              </span>
              <span class="layer-name">{{ getLayerName(obj) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { fabric } from 'fabric'
import { ElMessage } from 'element-plus'

const props = defineProps({
  contentId: {
    type: Number,
    required: true
  },
  initialText: {
    type: String,
    default: '在这里输入你的文案'
  }
})

const emit = defineEmits(['imageGenerated', 'imageExported'])

// Refs
const canvasRef = ref(null)
const canvas = ref(null)
const generating = ref(false)
const exporting = ref(false)
const backgroundImage = ref(null)

// Selected object and its properties
const selectedObject = ref(null)
const canvasObjects = ref([])

// Text properties
const textContent = ref('')
const fontSize = ref(48)
const lineHeight = ref(1.4)
const fontFamily = ref("'PingFang SC', sans-serif")
const textColor = ref('#1a2721')
const textBold = ref(true)
const textItalic = ref(false)
const textAlign = ref('center')

// Artistic text effects
const strokeColor = ref('rgba(0,0,0,0.4)')
const strokeWidth = ref(2)
const shadowBlur = ref(8)
const shadowX = ref(2)
const shadowY = ref(2)
const shadowColor = ref('rgba(0,0,0,0.5)')

// Logo properties
const logoVersion = ref('color')
const logoWidth = ref(120)
const logoOpacity = ref(90)

// Background properties
const bgOpacity = ref(100)

onMounted(() => {
  initCanvas()
  addInitialText()
})

onBeforeUnmount(() => {
  if (canvas.value) {
    canvas.value.dispose()
  }
})

function initCanvas() {
  canvas.value = new fabric.Canvas('fabricCanvas', {
    width: 1024,
    height: 1024,
    backgroundColor: '#f5f5f5'
  })

  // Listen to selection events
  canvas.value.on('selection:created', handleSelection)
  canvas.value.on('selection:updated', handleSelection)
  canvas.value.on('selection:cleared', () => {
    selectedObject.value = null
  })

  updateCanvasObjects()
}

function handleSelection(e) {
  selectedObject.value = e.selected[0]
  if (selectedObject.value) {
    loadObjectProperties(selectedObject.value)
  }
}

function loadObjectProperties(obj) {
  if (obj.type === 'text') {
    textContent.value = obj.text
    fontSize.value = obj.fontSize
    lineHeight.value = obj.lineHeight
    fontFamily.value = obj.fontFamily
    textColor.value = obj.fill
    textBold.value = obj.fontWeight === 'bold'
    textItalic.value = obj.fontStyle === 'italic'
    textAlign.value = obj.textAlign

    // 加载艺术字效果属性
    strokeColor.value = obj.stroke || 'rgba(0,0,0,0.4)'
    strokeWidth.value = obj.strokeWidth || 0
    if (obj.shadow) {
      shadowBlur.value = obj.shadow.blur || 0
      shadowX.value = obj.shadow.offsetX || 0
      shadowY.value = obj.shadow.offsetY || 0
      shadowColor.value = obj.shadow.color || 'rgba(0,0,0,0.5)'
    }
  } else if (obj.type === 'image') {
    logoWidth.value = obj.width * obj.scaleX
    logoOpacity.value = obj.opacity * 100
  }
}

function updateCanvasObjects() {
  canvasObjects.value = canvas.value.getObjects().map((obj, index) => ({
    id: obj.id || `obj-${index}`,
    type: obj.type,
    ...obj
  }))
}

function getLayerName(obj) {
  if (obj.id === 'background') return '背景图'
  if (obj.type === 'text') return obj.text.substring(0, 10) + '...'
  if (obj.type === 'image') return 'Logo'
  return '图层'
}

async function generateImage() {
  generating.value = true
  try {
    // 清空画布，移除所有旧内容
    canvas.value.clear()
    canvas.value.backgroundColor = '#f5f5f5'
    backgroundImage.value = null

    // 步骤1: 生成AI背景图
    const API_BASE = import.meta.env.VITE_API_BASE || 'https://weibo-daily-sentence.zeabur.app'
    const response = await fetch(`${API_BASE}/api/content/${props.contentId}/generate-image`, {
      method: 'POST'
    })
    const data = await response.json()

    if (data.success && data.image_url) {
      // 步骤2: 加载背景图
      await setBackgroundImage(data.image_url)

      // 步骤3: 分析背景亮度，智能选择Logo版本
      const brightness = await analyzeBackgroundBrightness()
      const smartLogoVersion = brightness > 128 ? 'color' : 'white' // 亮背景用原色，暗背景用反白

      // 步骤4: 添加艺术字文字（带描边和阴影）
      await addStyledText(props.initialText, brightness)

      // 步骤5: 自动添加Logo水印
      await addSmartLogo(smartLogoVersion)

      ElMessage.success('内容生成成功！背景、文字、Logo已自动配置')
      emit('imageGenerated', data.image_url)
    } else {
      throw new Error(data.message || '生成失败')
    }
  } catch (error) {
    ElMessage.error('生成失败: ' + error.message)
  } finally {
    generating.value = false
  }
}

// 分析背景图亮度
async function analyzeBackgroundBrightness() {
  if (!backgroundImage.value) return 128

  try {
    const imgElement = backgroundImage.value.getElement()
    const tempCanvas = document.createElement('canvas')
    const ctx = tempCanvas.getContext('2d')

    // 缩小取样提高性能
    tempCanvas.width = 100
    tempCanvas.height = 100
    ctx.drawImage(imgElement, 0, 0, 100, 100)

    const imageData = ctx.getImageData(0, 0, 100, 100)
    const data = imageData.data
    let totalBrightness = 0

    // 计算平均亮度
    for (let i = 0; i < data.length; i += 4) {
      const r = data[i]
      const g = data[i + 1]
      const b = data[i + 2]
      totalBrightness += (r + g + b) / 3
    }

    return totalBrightness / (100 * 100)
  } catch (error) {
    console.error('亮度分析失败:', error)
    return 128 // 默认中等亮度
  }
}

// 添加艺术字文字（带描边、阴影、渐变）
async function addStyledText(text, brightness) {
  // 根据背景亮度智能选择文字颜色
  const isDark = brightness < 128
  const textColor = isDark ? '#ffffff' : '#1a2721'
  const strokeColor = isDark ? 'rgba(0,0,0,0.5)' : 'rgba(255,255,255,0.8)'

  const styledText = new fabric.Text(text, {
    id: 'main-text',
    left: canvas.value.width / 2,
    top: canvas.value.height / 2,
    fontSize: 56,
    fontFamily: "'PingFang SC', sans-serif",
    fill: textColor,
    fontWeight: 'bold',
    textAlign: 'center',
    lineHeight: 1.5,
    originX: 'center',
    originY: 'center',
    // 艺术字效果
    stroke: strokeColor,
    strokeWidth: 3,
    shadow: {
      color: isDark ? 'rgba(0,0,0,0.6)' : 'rgba(0,0,0,0.3)',
      blur: 10,
      offsetX: 2,
      offsetY: 2
    }
  })

  canvas.value.add(styledText)
  canvas.value.renderAll()
  updateCanvasObjects()
}

// 智能添加Logo水印
async function addSmartLogo(version) {
  logoVersion.value = version
  const logoUrl = getLogoUrl(version)

  return new Promise((resolve) => {
    fabric.Image.fromURL(logoUrl, (img) => {
      if (!img) {
        resolve()
        return
      }

      img.set({
        id: 'smart-logo',
        left: canvas.value.width - 180,
        top: canvas.value.height - 100,
        scaleX: 0.35,
        scaleY: 0.35,
        opacity: 0.95
      })

      canvas.value.add(img)
      canvas.value.renderAll()
      updateCanvasObjects()
      resolve()
    }, { crossOrigin: 'anonymous' })
  })
}

function setBackgroundImage(url) {
  return new Promise((resolve, reject) => {
    fabric.Image.fromURL(url, (img) => {
      if (!img) {
        reject(new Error('图片加载失败'))
        return
      }

      // Remove existing background
      if (backgroundImage.value) {
        canvas.value.remove(backgroundImage.value)
      }

      // Scale to fit canvas
      const scale = Math.max(
        canvas.value.width / img.width,
        canvas.value.height / img.height
      )

      img.set({
        id: 'background',
        scaleX: scale,
        scaleY: scale,
        left: 0,
        top: 0,
        selectable: false,
        evented: false
      })

      canvas.value.add(img)
      canvas.value.sendToBack(img)
      backgroundImage.value = img
      canvas.value.renderAll()
      updateCanvasObjects()
      resolve()
    }, { crossOrigin: 'anonymous' })
  })
}

function addInitialText() {
  const text = new fabric.Text(props.initialText, {
    id: 'main-text',
    left: canvas.value.width / 2,
    top: canvas.value.height / 2,
    fontSize: 56,
    fontFamily: "'PingFang SC', sans-serif",
    fill: '#ffffff',
    fontWeight: 'bold',
    textAlign: 'center',
    lineHeight: 1.5,
    originX: 'center',
    originY: 'center',
    // 艺术字效果
    stroke: 'rgba(0,0,0,0.4)',
    strokeWidth: 2,
    shadow: {
      color: 'rgba(0,0,0,0.5)',
      blur: 8,
      offsetX: 2,
      offsetY: 2
    }
  })
  canvas.value.add(text)
  canvas.value.setActiveObject(text)
  canvas.value.renderAll()
  updateCanvasObjects()
}

function addText() {
  const text = new fabric.Text('双击编辑文字', {
    left: canvas.value.width / 2,
    top: canvas.value.height / 2,
    fontSize: 32,
    fontFamily: "'PingFang SC', sans-serif",
    fill: '#333333',
    originX: 'center',
    originY: 'center'
  })
  canvas.value.add(text)
  canvas.value.setActiveObject(text)
  canvas.value.renderAll()
  updateCanvasObjects()
}

async function addLogo() {
  const logoUrl = getLogoUrl(logoVersion.value)
  fabric.Image.fromURL(logoUrl, (img) => {
    img.set({
      left: canvas.value.width - 160,
      top: canvas.value.height - 80,
      scaleX: 0.3,
      scaleY: 0.3,
      opacity: logoOpacity.value / 100
    })
    canvas.value.add(img)
    canvas.value.setActiveObject(img)
    canvas.value.renderAll()
    updateCanvasObjects()
  })
}

function getLogoUrl(version) {
  // 这里应该返回你的 Logo 文件路径
  const logoMap = {
    color: '/PUDOW朴道水汇-横-原色.png',
    white: '/PUDOW朴道水汇-横-反白.png',
    black: '/PUDOW朴道水汇-横-墨稿.png'
  }
  return logoMap[version] || logoMap.color
}

function deleteSelected() {
  const activeObject = canvas.value.getActiveObject()
  if (activeObject && activeObject.id !== 'background') {
    canvas.value.remove(activeObject)
    canvas.value.renderAll()
    updateCanvasObjects()
  }
}

function selectLayer(obj) {
  const canvasObj = canvas.value.getObjects().find(o => (o.id || o) === obj.id)
  if (canvasObj) {
    canvas.value.setActiveObject(canvasObj)
    canvas.value.renderAll()
  }
}

// Update functions
function updateText() {
  if (selectedObject.value && selectedObject.value.type === 'text') {
    selectedObject.value.set('text', textContent.value)
    canvas.value.renderAll()
  }
}

function updateFontSize() {
  if (selectedObject.value && selectedObject.value.type === 'text') {
    selectedObject.value.set('fontSize', fontSize.value)
    canvas.value.renderAll()
  }
}

function updateLineHeight() {
  if (selectedObject.value && selectedObject.value.type === 'text') {
    selectedObject.value.set('lineHeight', lineHeight.value)
    canvas.value.renderAll()
  }
}

function updateFontFamily() {
  if (selectedObject.value && selectedObject.value.type === 'text') {
    selectedObject.value.set('fontFamily', fontFamily.value)
    canvas.value.renderAll()
  }
}

function updateTextColor() {
  if (selectedObject.value && selectedObject.value.type === 'text') {
    selectedObject.value.set('fill', textColor.value)
    canvas.value.renderAll()
  }
}

function updateTextStyle() {
  if (selectedObject.value && selectedObject.value.type === 'text') {
    selectedObject.value.set({
      fontWeight: textBold.value ? 'bold' : 'normal',
      fontStyle: textItalic.value ? 'italic' : 'normal'
    })
    canvas.value.renderAll()
  }
}

function updateTextAlign(align) {
  textAlign.value = align
  if (selectedObject.value && selectedObject.value.type === 'text') {
    selectedObject.value.set('textAlign', align)
    canvas.value.renderAll()
  }
}

// Artistic effects update functions
function updateStroke() {
  if (selectedObject.value && selectedObject.value.type === 'text') {
    selectedObject.value.set({
      stroke: strokeColor.value,
      strokeWidth: strokeWidth.value
    })
    canvas.value.renderAll()
  }
}

function updateShadow() {
  if (selectedObject.value && selectedObject.value.type === 'text') {
    selectedObject.value.set('shadow', {
      color: shadowColor.value,
      blur: shadowBlur.value,
      offsetX: shadowX.value,
      offsetY: shadowY.value
    })
    canvas.value.renderAll()
  }
}

function changeLogo() {
  if (selectedObject.value && selectedObject.value.type === 'image') {
    const logoUrl = getLogoUrl(logoVersion.value)
    const currentObj = selectedObject.value

    fabric.Image.fromURL(logoUrl, (img) => {
      img.set({
        left: currentObj.left,
        top: currentObj.top,
        scaleX: currentObj.scaleX,
        scaleY: currentObj.scaleY,
        opacity: currentObj.opacity,
        angle: currentObj.angle
      })
      canvas.value.remove(currentObj)
      canvas.value.add(img)
      canvas.value.setActiveObject(img)
      canvas.value.renderAll()
      updateCanvasObjects()
    })
  }
}

function updateLogoSize() {
  if (selectedObject.value && selectedObject.value.type === 'image') {
    const scale = logoWidth.value / selectedObject.value.width
    selectedObject.value.set({
      scaleX: scale,
      scaleY: scale
    })
    canvas.value.renderAll()
  }
}

function updateLogoOpacity() {
  if (selectedObject.value && selectedObject.value.type === 'image') {
    selectedObject.value.set('opacity', logoOpacity.value / 100)
    canvas.value.renderAll()
  }
}

function updateBgOpacity() {
  if (backgroundImage.value) {
    backgroundImage.value.set('opacity', bgOpacity.value / 100)
    canvas.value.renderAll()
  }
}

async function exportImage() {
  exporting.value = true
  try {
    // Deselect all objects
    canvas.value.discardActiveObject()
    canvas.value.renderAll()

    // Export as PNG
    const dataURL = canvas.value.toDataURL({
      format: 'png',
      quality: 1,
      multiplier: 1
    })

    // Download
    const link = document.createElement('a')
    link.download = `pudow-content-${props.contentId}-${Date.now()}.png`
    link.href = dataURL
    link.click()

    ElMessage.success('图片导出成功！')
    emit('imageExported', dataURL)
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.image-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--panel);
  border-radius: 8px;
  overflow: hidden;
}

.editor-header {
  padding: 16px;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.editor-header h3 {
  margin: 0;
  font-size: 16px;
}

.editor-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  border: 1px solid var(--line);
  background: white;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-icon:hover {
  background: var(--panel-soft);
  border-color: var(--green);
}

.btn-icon svg {
  width: 18px;
  height: 18px;
  color: var(--text);
}

.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.editor-body {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 0;
  overflow: hidden;
}

.canvas-container {
  position: relative;
  display: grid;
  place-items: center;
  background: #e5e5e5;
  overflow: auto;
  padding: 20px;
}

canvas {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-radius: 4px;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.95);
  display: grid;
  place-items: center;
  z-index: 10;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--line);
  border-top-color: var(--green);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-overlay p {
  margin-top: 16px;
  color: var(--muted);
}

.properties-panel {
  border-left: 1px solid var(--line);
  background: white;
  overflow: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: var(--faint);
}

.property-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.property-group h4 {
  margin: 0;
  font-size: 14px;
  color: var(--text);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--line);
}

.property-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.property-field label {
  font-size: 12px;
  color: var(--muted);
  font-weight: 500;
}

.property-field input,
.property-field select,
.property-field textarea {
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: 6px;
  font-size: 14px;
  outline: none;
}

.property-field textarea {
  resize: vertical;
  font-family: inherit;
  line-height: 1.5;
}

.property-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.color-picker {
  display: grid;
  grid-template-columns: 48px 1fr;
  gap: 8px;
}

.color-picker input[type="color"] {
  height: 36px;
  padding: 2px;
  cursor: pointer;
}

.color-input {
  font-family: monospace;
  text-transform: uppercase;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text);
  cursor: pointer;
}

.checkbox-label input {
  width: 16px;
  height: 16px;
  accent-color: var(--green);
}

.align-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}

.align-buttons button {
  padding: 8px;
  border: 1px solid var(--line);
  border-radius: 4px;
  background: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.align-buttons button.active,
.align-buttons button:hover {
  background: var(--green-soft);
  border-color: var(--green);
  color: var(--green-dark);
}

.layers-panel {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
}

.layers-panel h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
}

.layer-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.layer-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.layer-item:hover {
  background: var(--panel-soft);
}

.layer-item.active {
  background: var(--green-soft);
  color: var(--green-dark);
}

.layer-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.layer-icon svg {
  width: 100%;
  height: 100%;
}

.layer-name {
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 1200px) {
  .editor-body {
    grid-template-columns: 1fr;
  }

  .properties-panel {
    border-left: none;
    border-top: 1px solid var(--line);
    max-height: 400px;
  }
}
</style>
