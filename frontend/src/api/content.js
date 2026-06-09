import request from '@/utils/request'

// 生成内容池
export function generateContentPool(count = 30, autoGenerateImages = false) {
  return request.post('/content/generate', {
    count,
    auto_generate_images: autoGenerateImages
  })
}

// 获取内容列表
export function getContentList(params) {
  return request.get('/content/', { params })
}

// 获取内容详情
export function getContentDetail(id) {
  return request.get(`/content/${id}`)
}

// 获取单个内容（别名）
export function getContentById(id) {
  return request.get(`/content/${id}`)
}

// 生成图片
export function generateImage(id) {
  return request.post(`/content/${id}/generate-image`)
}

// 添加水印
export function addWatermark(id) {
  return request.post(`/content/${id}/add-watermark`)
}

// 处理内容（生成图片+水印）
export function processContent(id) {
  return request.post(`/content/${id}/process`)
}

// 删除内容
export function deleteContent(id) {
  return request.delete(`/content/${id}`)
}

// 审核内容
export function reviewContent(id, data) {
  return request.post(`/review/${id}/review`, data)
}

// 获取待审核数量
export function getPendingCount() {
  return request.get('/review/pending/count')
}

// 获取已通过数量
export function getApprovedCount() {
  return request.get('/review/approved/count')
}

// 发布内容
export function publishContent(contentId) {
  return request.post('/publish/', { content_id: contentId })
}

// 获取发布日志
export function getPublishLogs(params) {
  return request.get('/publish/logs', { params })
}

// 获取发布统计
export function getPublishStats() {
  return request.get('/publish/stats')
}

// 获取内容池状态
export function getPoolStatus() {
  return request.get('/content/pool/status')
}
