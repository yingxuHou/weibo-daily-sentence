<template>
  <div class="published-list">
    <!-- 统计卡片 -->
    <section class="stats-band" aria-label="发布统计">
      <article class="stat">
        <label>总发布数</label>
        <strong>{{ stats?.total_published || 0 }}</strong>
      </article>
      <article class="stat">
        <label>成功数 <span class="status approved">已发布</span></label>
        <strong>{{ stats?.success_count || 0 }}</strong>
      </article>
      <article class="stat">
        <label>失败数 <span class="status rejected">需重试</span></label>
        <strong>{{ stats?.failed_count || 0 }}</strong>
      </article>
      <article class="stat">
        <label>成功率</label>
        <strong>{{ stats?.success_rate || 0 }}%</strong>
      </article>
    </section>

    <!-- 发布日志表格 -->
    <div class="table-section">
      <div class="panel-title" style="margin-bottom: 14px;">
        <h2>发布日志</h2>
        <button class="btn" @click="loadData" :disabled="loading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon"><path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 3v6h-6"/></svg>
          刷新
        </button>
      </div>

      <el-table :data="logs" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="日志ID" width="80" />
        <el-table-column prop="content_id" label="内容ID" width="100" />
        <el-table-column prop="weibo_id" label="微博ID" width="200">
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

      <div class="pagination" v-if="logs.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadLogs"
          @size-change="loadLogs"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPublishLogs, getPublishStats } from '@/api/content'

const loading = ref(false)
const logs = ref([])
const stats = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

onMounted(() => { loadData() })

async function loadData() {
  await Promise.all([loadLogs(), loadStats()])
}

async function loadLogs() {
  loading.value = true
  try {
    const params = { skip: (currentPage.value - 1) * pageSize.value, limit: pageSize.value }
    const data = await getPublishLogs(params)
    logs.value = data
    total.value = data.length
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    stats.value = await getPublishStats()
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

function formatTime(time) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}
</script>

<style scoped>
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

.table-section {
  padding: 18px 28px 28px;
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.panel-title h2 {
  margin: 0;
  font-size: 16px;
}

.icon {
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
}

.link {
  color: var(--blue);
  text-decoration: none;
}

.link:hover { text-decoration: underline; }
.faint { color: var(--faint); }

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
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
