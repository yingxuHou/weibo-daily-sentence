import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/content',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '内容生成' }
      },
      {
        path: 'content',
        name: 'ContentList',
        component: () => import('@/views/ContentList.vue'),
        meta: { title: '审核池' }
      },
      {
        path: 'editor/:id',
        name: 'ImageEditor',
        component: () => import('@/views/EditorPage.vue'),
        meta: { title: '图片编辑' }
      },
      {
        path: 'published',
        name: 'PublishedList',
        component: () => import('@/views/PublishedList.vue'),
        meta: { title: '发布记录' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
