<template>
  <div class="workbench">
    <!-- 左侧：内容列表 -->
    <div class="list-panel">
      <div class="panel-head">
        <div class="panel-title">
          <h2>内容列表</h2>
          <span class="batch-count">已选 {{ selected.size }} 条</span>
        </div>

        <div class="controls">
          <label class="search">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon">
              <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.3-4.3"/>
            </svg>
            <input v-model="searchQuery" type="search" placeholder="搜索文案、编号、状态" @input="applyFilters">
          </label>
          <label class="select">
            <select v-model="styleFilter" @change="applyFilters" aria-label="图片风格">
              <option value="all">全部风格</option>
              <option value="清新">清新</option>
              <option value="温暖">温暖</option>
              <option value="治愈">治愈</option>
            </select>
          </label>
          <label class="select">
            <select v-model="sortBy" @change="applyFilters" aria-label="排序">
              <option value="new">最新生成</option>
              <option value="id">文案序号</option>
            </select>
          </label>
        </div>

        <!-- 状态 Tab -->
        <div class="tabs" role="tablist" aria-label="状态筛选">
          <button v-for="tab in statusTabs" :key="tab.value"
            class="tab" :class="{ active: activeStatus === tab.value }"
            @click="activeStatus = tab.value">{{ tab.label }}</button>
        </div>
      </div>

      <!-- 批量操作栏 -->
      <div class="bulkbar">
        <label class="bulkbar-left">
          <input class="check" type="checkbox" :checked="allChecked" @change="toggleSelectAll">
          <span>本页批量操作</span>
        </label>
        <div class="bulkbar-actions">
          <button class="btn" @click="bulkReview(true)" :disabled="selected.size === 0">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon"><path d="M20 6L9 17l-5-5"/></svg>
            通过
          </button>
          <button class="btn danger" @click="bulkReview(false)" :disabled="selected.size === 0">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon"><path d="M18 6L6 18"/><path d="M6 6l12 12"/></svg>
            拒绝
          </button>
        </div>
      </div>

      <!-- 内容列表 -->
      <div class="content-list" v-loading="loading">
        <div v-if="!loading && filteredContents.length === 0" class="empty-list">暂无内容</div>
        <button
          v-for="item in filteredContents" :key="item.id"
          class="content-row" :class="{ active: activeId === item.id }"
          @click="selectItem(item)"
        >
          <input class="check" type="checkbox"
            :checked="selected.has(item.id)"
            @click.stop
            @change="toggleItem(item.id, $event.target.checked)"
            aria-label="选择">
          <span class="thumb" :class="thumbClass(item.id)">
            <span>#{{ item.id }}</span>
          </span>
          <span class="row-copy">
            <span class="row-meta">
              <span class="status" :class="statusClass(item.status)">{{ item.status }}</span>
              <span>{{ item.logo_version === 'color' ? '原色' : (item.logo_version === 'white' ? '反白' : '无Logo') }}</span>
              <span>文案 #{{ item.sentence_id }}</span>
            </span>
            <strong>{{ item.text }}</strong>
            <p>{{ item.note || '' }}</p>
          </span>
          <span class="quality">
            <b>{{ item.quality || 80 }}</b>
            <span class="quality-track"><span :style="{ width: (item.quality || 80) + '%' }"></span></span>
          </span>
        </button>
      </div>
    </div>

    <!-- 右侧：预览/审核面板 -->
    <aside class="preview-panel" v-if="activeItem">
      <div class="panel-head">
        <div class="panel-title">
          <h2>单条审核</h2>
          <span class="status" :class="statusClass(activeItem.status)">{{ activeItem.status }}</span>
        </div>
      </div>
      <div class="preview-scroll">
        <!-- 图片预览 -->
        <div class="preview-image">
          <img v-if="activeItem.image_url" :src="getImageUrl(activeItem.image_url)" alt="配图" class="real-image" />
          <template v-else>
            <p>{{ activeItem.text }}</p>
            <img class="watermark" src="/PUDOW朴道水汇-横-原色.png" alt="PUDOW">
          </template>
        </div>

        <!-- 文案编辑 -->
        <div class="detail-block">
          <h3>文案编辑</h3>
          <textarea class="sentence-editor" v-model="editText" rows="3"></textarea>
        </div>

        <!-- 生成参数 -->
        <div class="detail-block">
          <h3>生成参数</h3>
          <div class="form-grid">
            <div class="field">
              <label for="styleSelect">图片风格</label>
              <select id="styleSelect" v-model="editStyle">
                <option>清新</option>
                <option>温暖</option>
                <option>治愈</option>
                <option>简约</option>
              </select>
            </div>
            <div class="field">
              <label for="sizeSelect">发布尺寸</label>
              <select id="sizeSelect">
                <option>1080 x 1080</option>
                <option>1440 x 1080</option>
              </select>
            </div>
            <div class="field">
              <label for="logoSelect">Logo 版本</label>
              <select id="logoSelect" v-model="editLogo">
                <option>自动识别</option>
                <option>原色</option>
                <option>反白</option>
                <option>墨稿</option>
              </select>
            </div>
            <div class="field">
              <label>发布时间</label>
              <input value="明日 08:00" readonly>
            </div>
          </div>
        </div>

        <!-- 视觉校准 -->
        <div class="detail-block">
          <h3>视觉校准</h3>
          <div class="style-row">
            <div class="swatches" aria-label="色彩方案">
              <button class="swatch sw-one" title="品牌绿"></button>
              <button class="swatch sw-two" title="晨光金"></button>
              <button class="swatch sw-three" title="水蓝"></button>
              <button class="swatch sw-four" title="暖红"></button>
            </div>
            <label class="switch">
              <input type="checkbox" checked>
              自动加水印
            </label>
          </div>
        </div>

        <!-- 审核按钮 -->
        <div class="audit-actions">
          <button class="btn" @click="openEditor" :disabled="auditing">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            编辑图片
          </button>
          <button class="btn danger" @click="handleReject" :disabled="auditing">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon"><path d="M18 6L6 18"/><path d="M6 6l12 12"/></svg>
            拒绝
          </button>
          <button class="btn primary" @click="handleApprove" :disabled="auditing">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon"><path d="M20 6L9 17l-5-5"/></svg>
            通过审核
          </button>
        </div>
      </div>
    </aside>

    <!-- 空状态：未选中 -->
    <aside class="preview-panel" v-else>
      <div class="panel-head">
        <div class="panel-title"><h2>单条审核</h2></div>
      </div>
      <div class="empty-preview">
        <p>选择左侧内容进行审核</p>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getContentList, reviewContent, deleteContent, processContent } from '@/api/content'

const router = useRouter()

const loading = ref(false)
const auditing = ref(false)
const contents = ref([])
const activeId = ref(null)
const selected = reactive(new Set())
const searchQuery = ref('')
const styleFilter = ref('all')
const sortBy = ref('new')
const activeStatus = ref('all')

const editText = ref('')
const editStyle = ref('清新')
const editLogo = ref('自动识别')

const statusTabs = [
  { value: 'all', label: '全部' },
  { value: '待审核', label: '待审核' },
  { value: '已通过', label: '已通过' },
  { value: '已拒绝', label: '已拒绝' },
  { value: '已发布', label: '已发布' },
]

const activeItem = computed(() => {
  return contents.value.find(c => c.id === activeId.value) || null
})

const filteredContents = computed(() => {
  let result = [...contents.value]

  // Status filter
  if (activeStatus.value !== 'all') {
    result = result.filter(c => c.status === activeStatus.value)
  }

  // Search filter
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    result = result.filter(c =>
      c.text.toLowerCase().includes(q) ||
      String(c.id).includes(q) ||
      String(c.sentence_id).includes(q) ||
      c.status.includes(q)
    )
  }

  // Sort
  if (sortBy.value === 'new') {
    result.sort((a, b) => b.id - a.id)
  } else {
    result.sort((a, b) => a.sentence_id - b.sentence_id)
  }

  return result
})

const allChecked = computed(() => {
  return filteredContents.value.length > 0 && filteredContents.value.every(c => selected.has(c.id))
})

// Watch active item to sync edit fields
watch(activeItem, (item) => {
  if (item) {
    editText.value = item.text
    editStyle.value = '清新'
    editLogo.value = item.logo_version === 'color' ? '原色' : (item.logo_version === 'white' ? '反白' : '自动识别')
  }
})

onMounted(() => { loadContents() })

async function loadContents() {
  loading.value = true
  try {
    const params = { skip: 0, limit: 100 }
    if (activeStatus.value !== 'all') params.status = activeStatus.value
    const data = await getContentList(params)
    contents.value = data.map(c => ({
      ...c,
      note: c.reject_reason || noteForStatus(c),
      quality: qualityScore(c),
    }))
    if (!activeId.value || !contents.value.find(c => c.id === activeId.value)) {
      activeId.value = contents.value[0]?.id || null
    }
  } catch (error) {
    ElMessage.error('加载内容失败')
  } finally {
    loading.value = false
  }
}

function noteForStatus(c) {
  if (c.status === '已通过') return '已通过，可进入发布队列。'
  if (c.status === '已拒绝') return '建议检查内容质量。'
  if (c.status === '已发布') return '已发布成功。'
  if (!c.image_url) return '图片待生成。'
  return '文案情绪积极。'
}

function qualityScore(c) {
  if (c.status === '已发布') return 89 + Math.floor(Math.random() * 10)
  if (c.status === '已通过') return 85 + Math.floor(Math.random() * 12)
  if (c.status === '已拒绝') return 50 + Math.floor(Math.random() * 30)
  if (c.image_url) return 70 + Math.floor(Math.random() * 25)
  return 60 + Math.floor(Math.random() * 25)
}

function selectItem(item) {
  activeId.value = item.id
}

function toggleItem(id, checked) {
  checked ? selected.add(id) : selected.delete(id)
}

function toggleSelectAll(e) {
  filteredContents.value.forEach(c => {
    e.target.checked ? selected.add(c.id) : selected.delete(c.id)
  })
}

function applyFilters() {
  // Filters are reactive in computed, no extra work needed
}

function openEditor() {
  if (!activeItem.value) return
  router.push(`/editor/${activeItem.value.id}`)
}

async function handleApprove() {
  if (!activeItem.value) return
  auditing.value = true
  try {
    await reviewContent(activeItem.value.id, { approved: true, reviewer_id: 1 })
    ElMessage.success('审核通过')
    await loadContents()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    auditing.value = false
  }
}

async function handleReject() {
  if (!activeItem.value) return
  try {
    const result = await ElMessageBox.prompt('请输入拒绝原因', '拒绝内容', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '请输入拒绝原因'
    })
    auditing.value = true
    await reviewContent(activeItem.value.id, {
      approved: false,
      reject_reason: result.value,
      reviewer_id: 1
    })
    ElMessage.success('已拒绝')
    await loadContents()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  } finally {
    auditing.value = false
  }
}

async function bulkReview(approved) {
  if (selected.size === 0) return
  auditing.value = true
  try {
    let rejectReason = ''
    if (!approved) {
      const result = await ElMessageBox.prompt('请输入批量拒绝原因', '批量拒绝', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
      })
      rejectReason = result.value
    }
    const ids = [...selected]
    for (const id of ids) {
      try {
        await reviewContent(id, { approved, reject_reason: rejectReason, reviewer_id: 1 })
      } catch (e) { /* continue */ }
    }
    selected.clear()
    ElMessage.success(approved ? `已通过 ${ids.length} 条内容` : `已拒绝 ${ids.length} 条内容`)
    await loadContents()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  } finally {
    auditing.value = false
  }
}

function getImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('/')) return `http://localhost:8000${url}`
  return url
}

function statusClass(status) {
  const map = { '待审核': 'pending', '已通过': 'approved', '已拒绝': 'rejected', '已发布': 'published' }
  return map[status] || 'pending'
}

function thumbClass(id) {
  const v = id % 3
  if (v === 0) return ''
  if (v === 1) return 'alt'
  return 'night'
}
</script>

<style scoped>
.workbench {
  min-height: 0;
  padding: 18px 28px 28px;
  display: grid;
  grid-template-columns: minmax(460px, 1fr) 380px;
  gap: 18px;
  height: calc(100vh - 72px);
}

/* ---- List Panel ---- */
.list-panel,
.preview-panel {
  min-width: 0;
  min-height: 0;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
}

.panel-head {
  padding: 16px;
  border-bottom: 1px solid var(--line);
  display: grid;
  gap: 14px;
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.panel-title h2 {
  margin: 0;
  font-size: 16px;
  line-height: 1.3;
}

.batch-count {
  color: var(--muted);
  font-size: 13px;
  white-space: nowrap;
}

.controls {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) 132px 132px;
  gap: 10px;
}

.search,
.select {
  height: 38px;
  border: 1px solid var(--line);
  border-radius: 7px;
  background: #ffffff;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 11px;
  min-width: 0;
}

.search input,
.select select {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--text);
  font-size: 14px;
}

.icon {
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  color: var(--faint);
}

.tabs {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tab {
  min-height: 34px;
  border-radius: 7px;
  padding: 0 12px;
  background: #edf2ef;
  color: var(--muted);
  font-size: 13px;
  transition: all 0.15s;
}

.tab.active {
  background: var(--green-soft);
  color: var(--green-dark);
  box-shadow: inset 0 0 0 1px #b8dccf;
}

.bulkbar {
  padding: 10px 16px;
  border-bottom: 1px solid var(--line);
  background: var(--panel-soft);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 50px;
  flex-shrink: 0;
}

.bulkbar-left,
.bulkbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.check {
  width: 18px;
  height: 18px;
  accent-color: var(--green);
  flex: 0 0 auto;
}

/* ---- Content List ---- */
.content-list {
  padding: 10px;
  overflow: auto;
  display: grid;
  gap: 10px;
  flex: 1;
}

.empty-list {
  text-align: center;
  color: var(--faint);
  padding: 40px 0;
  font-size: 14px;
}

.content-row {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #ffffff;
  padding: 10px;
  display: grid;
  grid-template-columns: 18px 92px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s;
}

.content-row:hover,
.content-row.active {
  border-color: #9ccbb8;
  background: #fbfefc;
}

.thumb {
  width: 92px;
  aspect-ratio: 1;
  border-radius: 7px;
  overflow: hidden;
  background: linear-gradient(135deg, #cde7df 0%, #f3dfb4 52%, #b7cde2 100%);
  position: relative;
  display: grid;
  place-items: end;
  padding: 8px;
}

.thumb.alt {
  background: linear-gradient(135deg, #e7d5b5 0%, #a8c6be 52%, #d8e5ee 100%);
}

.thumb.night {
  background: linear-gradient(135deg, #33413d 0%, #52736a 55%, #d3a45d 100%);
}

.thumb::before {
  content: "";
  position: absolute;
  inset: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, .34);
}

.thumb span {
  position: relative;
  font-size: 10px;
  color: rgba(24, 39, 34, .72);
  background: rgba(255, 255, 255, .64);
  border-radius: 4px;
  padding: 2px 4px;
}

.row-copy {
  min-width: 0;
}

.row-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--faint);
  font-size: 12px;
  margin-bottom: 7px;
  flex-wrap: wrap;
}

.row-copy strong {
  display: block;
  font-size: 14px;
  line-height: 1.55;
  font-weight: 650;
  color: var(--text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.row-copy p {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.45;
}

.quality {
  width: 88px;
  display: grid;
  gap: 6px;
  justify-items: end;
}

.quality b {
  font-size: 13px;
  color: var(--green-dark);
}

.quality-track {
  width: 78px;
  height: 6px;
  border-radius: 999px;
  background: #e9efec;
  overflow: hidden;
}

.quality-track span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--green);
}

/* ---- Preview Panel ---- */
.preview-panel {
  overflow: hidden;
}

.preview-scroll {
  overflow: auto;
  padding: 16px;
  display: grid;
  gap: 16px;
  flex: 1;
}

.preview-image {
  aspect-ratio: 1;
  border-radius: 8px;
  background: linear-gradient(135deg, #cce5dc 0%, #f4e0b6 54%, #bed5e7 100%);
  position: relative;
  overflow: hidden;
  display: grid;
  place-items: center;
  padding: 28px;
  color: rgba(25, 44, 38, .86);
}

.preview-image::before {
  content: "";
  position: absolute;
  width: 54%;
  aspect-ratio: 1;
  border-radius: 50%;
  background: rgba(255, 255, 255, .34);
  top: 16%;
  left: 15%;
  box-shadow: 80px 90px 0 rgba(35, 122, 97, .1);
}

.preview-image p {
  position: relative;
  max-width: 260px;
  margin: 0;
  font-size: 25px;
  line-height: 1.55;
  font-weight: 700;
  text-align: center;
}

.real-image {
  position: relative;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
}

.watermark {
  position: absolute;
  right: 18px;
  bottom: 18px;
  height: 26px;
  max-width: 138px;
  object-fit: contain;
  opacity: .92;
  background: rgba(255, 255, 255, .55);
  border-radius: 4px;
  padding: 3px 6px;
  z-index: 2;
}

.detail-block {
  border-top: 1px solid var(--line);
  padding-top: 14px;
  display: grid;
  gap: 10px;
}

.detail-block:first-of-type {
  border-top: 0;
  padding-top: 0;
}

.detail-block h3 {
  margin: 0;
  font-size: 14px;
  line-height: 1.35;
}

.sentence-editor {
  width: 100%;
  min-height: 92px;
  resize: vertical;
  border: 1px solid var(--line);
  border-radius: 7px;
  padding: 10px;
  line-height: 1.6;
  color: var(--text);
  outline: 0;
  font-size: 14px;
  background: #ffffff;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.field {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.field label {
  color: var(--muted);
  font-size: 12px;
}

.field input,
.field select {
  height: 36px;
  border: 1px solid var(--line);
  border-radius: 7px;
  padding: 0 10px;
  min-width: 0;
  background: #ffffff;
  color: var(--text);
  outline: 0;
}

.style-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.swatches {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.swatch {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  border: 2px solid #ffffff;
  box-shadow: 0 0 0 1px var(--line-strong);
  cursor: pointer;
}

.sw-one { background: #217a61; }
.sw-two { background: #e0b05a; }
.sw-three { background: #5b8ab7; }
.sw-four { background: #bd6a60; }

.switch {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--muted);
  font-size: 13px;
}

.switch input {
  width: 38px;
  height: 20px;
  accent-color: var(--green);
}

.audit-actions {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  position: sticky;
  bottom: 0;
  padding-top: 10px;
  background: var(--panel);
}

.empty-preview {
  flex: 1;
  display: grid;
  place-items: center;
  color: var(--faint);
  font-size: 14px;
}

/* ---- Responsive ---- */
@media (max-width: 1180px) {
  .workbench {
    grid-template-columns: 1fr;
    height: auto;
  }

  .preview-panel {
    min-height: 680px;
  }
}

@media (max-width: 760px) {
  .workbench {
    padding: 12px 16px 18px;
  }

  .controls {
    grid-template-columns: 1fr;
  }

  .bulkbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .content-row {
    grid-template-columns: 18px 76px minmax(0, 1fr);
  }

  .thumb {
    width: 76px;
  }

  .quality {
    grid-column: 2 / -1;
    width: 100%;
    justify-items: start;
  }

  .quality-track {
    width: 100%;
  }

  .form-grid,
  .audit-actions {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 500px) {
  .preview-image p {
    font-size: 20px;
  }
}
</style>
