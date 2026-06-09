import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getContentList,
  getPendingCount,
  getApprovedCount,
  getPoolStatus
} from '@/api/content'

export const useContentStore = defineStore('content', () => {
  const contents = ref([])
  const pendingCount = ref(0)
  const approvedCount = ref(0)
  const poolStatus = ref(null)
  const loading = ref(false)

  // 获取内容列表
  async function fetchContents(params) {
    loading.value = true
    try {
      contents.value = await getContentList(params)
    } finally {
      loading.value = false
    }
  }

  // 刷新统计数据
  async function refreshStats() {
    try {
      const [pending, approved, pool] = await Promise.all([
        getPendingCount(),
        getApprovedCount(),
        getPoolStatus()
      ])
      pendingCount.value = pending.pending_count
      approvedCount.value = approved.approved_count
      poolStatus.value = pool
    } catch (error) {
      console.error('刷新统计失败:', error)
    }
  }

  return {
    contents,
    pendingCount,
    approvedCount,
    poolStatus,
    loading,
    fetchContents,
    refreshStats
  }
})
