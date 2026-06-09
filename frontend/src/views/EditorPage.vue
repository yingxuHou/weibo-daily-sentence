<template>
  <div class="editor-page">
    <div class="page-header">
      <button class="btn-back" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        返回列表
      </button>
      <div class="header-info">
        <h1>编辑内容 #{{ contentId }}</h1>
        <span class="status-badge" :class="statusClass">{{ content?.status || '加载中' }}</span>
      </div>
    </div>

    <div class="editor-container" v-loading="loading">
      <ImageEditor
        v-if="content"
        :contentId="contentId"
        :initialText="content.text"
        @imageGenerated="handleImageGenerated"
        @imageExported="handleImageExported"
      />
      <div v-else class="loading-placeholder">
        <p>正在加载内容...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ImageEditor from '@/components/ImageEditor.vue'
import { getContentById } from '@/api/content'

const route = useRoute()
const router = useRouter()

const contentId = parseInt(route.params.id)
const loading = ref(true)
const content = ref(null)

onMounted(async () => {
  await loadContent()
})

async function loadContent() {
  loading.value = true
  try {
    // 调用 API 获取内容详情
    const data = await getContentById(contentId)
    content.value = data
  } catch (error) {
    ElMessage.error('加载内容失败')
    goBack()
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/content')
}

function handleImageGenerated(imageUrl) {
  console.log('Image generated:', imageUrl)
  ElMessage.success('背景图已生成！')
}

function handleImageExported(dataUrl) {
  console.log('Image exported:', dataUrl.substring(0, 50) + '...')
  ElMessage.success('图片已导出！')
}

const statusClass = computed(() => {
  const map = {
    '待审核': 'pending',
    '已通过': 'approved',
    '已拒绝': 'rejected',
    '已发布': 'published'
  }
  return map[content.value?.status] || 'pending'
})
</script>

<style scoped>
.editor-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}

.page-header {
  padding: 16px 28px;
  background: var(--panel);
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: white;
  color: var(--text);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-back:hover {
  background: var(--panel-soft);
  border-color: var(--green);
}

.btn-back svg {
  width: 18px;
  height: 18px;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.header-info h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.approved {
  background: #d4edda;
  color: #155724;
}

.status-badge.rejected {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.published {
  background: #d1ecf1;
  color: #0c5460;
}

.editor-container {
  flex: 1;
  padding: 20px 28px;
  overflow: auto;
  min-height: 0;
}

.loading-placeholder {
  display: grid;
  place-items: center;
  height: 100%;
  color: var(--faint);
}
</style>
