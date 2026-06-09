<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <section class="stats-band" aria-label="核心指标">
      <article class="stat">
        <label>待审核 <span class="status pending">需要处理</span></label>
        <strong>{{ poolStatus?.pending || 0 }}</strong>
        <small>其中部分图片待重新生成</small>
      </article>
      <article class="stat">
        <label>已通过 <span class="status approved">可发布</span></label>
        <strong>{{ poolStatus?.approved || 0 }}</strong>
        <small>预计可支撑 {{ poolStatus?.approved || 0 }} 天发布</small>
      </article>
      <article class="stat">
        <label>发布成功率 <span class="status published">近 30 天</span></label>
        <strong>{{ publishStats?.success_rate || 0 }}%</strong>
        <small>失败 {{ publishStats?.failed_count || 0 }} 次</small>
      </article>
      <article class="stat">
        <label>内容池总数 <span class="status approved">储备量</span></label>
        <strong>{{ poolStatus?.total || 0 }}</strong>
        <small>待审核 + 已通过</small>
      </article>
    </section>

    <!-- 内容池预警 -->
    <el-alert
      v-if="poolStatus?.warning"
      type="warning"
      title="内容池预警"
      :description="`当前可发布内容仅剩 ${poolStatus?.approved} 条，建议及时补充内容`"
      show-icon
      :closable="false"
      style="margin: 0 28px 18px; max-width: calc(100% - 56px);"
    />

    <!-- 快捷操作 -->
    <div class="actions-section">
      <h2 class="section-title">快捷操作</h2>
      <div class="actions-grid">
        <button class="btn primary" @click="handleGenerateContent" :disabled="generating">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon"><path d="M12 5v14"/><path d="M5 12h14"/></svg>
          {{ generating ? '生成中...' : '生成 30 条' }}
        </button>
        <button class="btn" @click="$router.push('/content')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
          审核内容
        </button>
        <button class="btn" @click="$router.push('/published')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg>
          查看发布记录
        </button>
      </div>
    </div>

    <!-- 最近发布 -->
    <div class="recent-section">
      <h2 class="section-title">最近发布</h2>
      <el-table :data="recentLogs" stripe style="width: 100%">
        <el-table-column prop="id" label="日志ID" width="80" />
        <el-table-column prop="content_id" label="内容ID" width="100" />
        <el-table-column prop="weibo_id" label="微博ID" width="180">
          <template #default="{ row }">
            <a v-if="row.weibo_id" :href="`https://weibo.com/${row.weibo_id}`" target="_blank" class="link">
              {{ row.weibo_id }}
            </a>
            <span v-else class="faint">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <span class="status" :class="row.status === '成功' ? 'approved' : 'rejected'">{{ row.status }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="published_at" label="发布时间" width="180">
          <template #default="{ row }">{{ formatTime(row.published_at) }}</template>
        </el-table-column>
        <el-table-column prop="error_msg" label="错误信息" show-overflow-tooltip />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, h } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useContentStore } from '@/stores/content'
import { generateContentPool, getPublishStats, getPublishLogs } from '@/api/content'

const contentStore = useContentStore()
const poolStatus = ref(null)
const publishStats = ref(null)
const recentLogs = ref([])
const generating = ref(false)

onMounted(() => { loadData() })

async function loadData() {
  try {
    await contentStore.refreshStats()
    poolStatus.value = contentStore.poolStatus
    const stats = await getPublishStats()
    publishStats.value = stats
    const logs = await getPublishLogs({ skip: 0, limit: 10 })
    recentLogs.value = logs
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

async function handleGenerateContent() {
  try {
    const result = await ElMessageBox({
      title: '生成内容池',
      message: h('div', null, [
        h('p', { style: 'margin-bottom: 12px; font-size: 14px;' }, '请配置生成参数：'),
        h('div', { style: 'margin-bottom: 12px;' }, [
          h('label', { style: 'display: block; margin-bottom: 6px; font-size: 13px; color: #666;' }, '生成数量：'),
          h('input', {
            type: 'number',
            value: '30',
            min: '1',
            max: '100',
            id: 'countInput',
            style: 'width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;'
          })
        ]),
        h('div', { style: 'display: flex; align-items: center; gap: 8px; padding: 12px; background: #f5f5f5; border-radius: 4px;' }, [
          h('input', {
            type: 'checkbox',
            id: 'autoGenCheckbox',
            checked: true,
            style: 'width: 18px; height: 18px; cursor: pointer;'
          }),
          h('label', {
            for: 'autoGenCheckbox',
            style: 'flex: 1; font-size: 14px; cursor: pointer; user-select: none;'
          }, '自动生成 AI 图片（每张约 30-60 秒）')
        ]),
        h('p', { style: 'margin-top: 12px; font-size: 12px; color: #999;' }, '提示：勾选后会自动为每条内容生成 AI 背景图、文字和 Logo，整个过程可能需要较长时间。')
      ]),
      confirmButtonText: '开始生成',
      cancelButtonText: '取消',
      beforeClose: (action, instance, done) => {
        if (action === 'confirm') {
          const count = document.getElementById('countInput').value
          const autoGen = document.getElementById('autoGenCheckbox').checked
          if (!count || count < 1) {
            ElMessage.warning('请输入有效的生成数量')
            return
          }
          instance.confirmButtonLoading = true
          instance.confirmButtonText = '生成中...'
          done()
        } else {
          done()
        }
      }
    })

    const count = parseInt(document.getElementById('countInput').value)
    const autoGen = document.getElementById('autoGenCheckbox').checked

    generating.value = true

    if (autoGen) {
      ElMessage.info(`正在生成 ${count} 条内容并自动配图，预计需要 ${Math.ceil(count * 0.75)} 分钟，请耐心等待...`)
    }

    const res = await generateContentPool(count, autoGen)

    if (res.count === 0) {
      ElMessage.warning('生成了 0 条内容，可能是 sentence.md 文件未找到或数据库错误，请检查后端日志')
    } else {
      if (autoGen) {
        ElMessage.success(`成功生成 ${res.count} 条内容，并自动配图完成！`)
      } else {
        ElMessage.success(`成功生成 ${res.count} 条内容`)
      }
    }
    await loadData()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      console.error('生成失败:', error)
      ElMessage.error(`生成失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
    }
  } finally {
    generating.value = false
  }
}

function formatTime(time) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}
</script>

<style scoped>
.dashboard {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.stats-band {
  padding: 18px 28px;
  display: grid;
  grid-template-columns: repeat(4, minmax(150px, 1fr));
  gap: 14px;
  border-bottom: 1px solid var(--line);
  background: #fbfcfb;
}

.stat {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
  min-height: 104px;
  display: grid;
  align-content: space-between;
  box-shadow: 0 8px 24px rgba(30, 48, 42, .04);
}

.stat label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--muted);
  font-size: 13px;
}

.stat strong {
  display: block;
  margin-top: 10px;
  font-size: 30px;
  line-height: 1;
}

.stat small {
  margin-top: 8px;
  color: var(--faint);
  font-size: 12px;
}

.actions-section {
  padding: 18px 28px;
}

.section-title {
  font-size: 16px;
  margin-bottom: 14px;
}

.actions-grid {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.icon {
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
}

.recent-section {
  padding: 0 28px 28px;
  flex: 1;
}

.link {
  color: var(--blue);
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.faint {
  color: var(--faint);
}

@media (max-width: 1180px) {
  .stats-band {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 500px) {
  .stats-band {
    grid-template-columns: 1fr;
  }
}
</style>
