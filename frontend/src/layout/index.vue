<template>
  <div class="app-shell">
    <!-- 侧边栏 -->
    <aside class="sidebar" aria-label="主导航">
      <div class="brand">
        <div class="brand-mark">
          <img src="/PUDOW朴道-原色.png" alt="PUDOW" />
        </div>
        <div>
          <strong>PUDOW 运营台</strong>
          <span>每日一句内容流水线</span>
        </div>
      </div>

      <nav class="nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
          :title="item.title"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-icon">
            <path v-if="item.icon === 'review'" d="M9 11l3 3L22 4 M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
            <path v-else-if="item.icon === 'generate'" d="M12 3v18 M3 12h18 M5 5l14 14" />
            <path v-else-if="item.icon === 'queue'" d="M22 2L11 13 M22 2l-7 20-4-9-9-4 20-7z" />
            <path v-else-if="item.icon === 'report'" d="M3 3v18h18 M7 15l4-4 3 3 5-7" />
            <path v-else-if="item.icon === 'settings'" d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.6-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1A2 2 0 1 1 7.1 4l.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1A2 2 0 1 1 19.9 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" />
          </svg>
          <span>{{ item.title }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <p>本月内容池储备 {{ poolStatus?.approved || 0 }} / {{ poolStatus?.total || 30 }}，建议审核通过不少于 7 条。</p>
        <div class="mini-meter" aria-hidden="true">
          <span :style="{ width: meterPercent + '%' }"></span>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main">
      <header class="topbar">
        <div class="page-title">
          <h1>{{ currentPageTitle }}</h1>
          <p>{{ subtitle }}</p>
        </div>
        <div class="top-actions">
          <slot name="top-actions" />
        </div>
      </header>

      <div class="content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useContentStore } from '@/stores/content'

const route = useRoute()
const contentStore = useContentStore()

const menuItems = [
  { path: '/content', title: '审核池', icon: 'review' },
  { path: '/dashboard', title: '内容生成', icon: 'generate' },
  { path: '/published', title: '发布队列', icon: 'queue' },
  { path: '/settings', title: '系统设置', icon: 'settings' },
]

const currentPageTitle = computed(() => {
  const map = {
    '/dashboard': '内容生成',
    '/content': '审核池',
    '/published': '发布队列',
    '/settings': '系统设置',
  }
  return map[route.path] || '审核池'
})

const subtitle = computed(() => {
  const now = new Date()
  const dateStr = now.toISOString().slice(0, 10)
  const hours = now.getHours()
  const minutes = now.getMinutes()
  const timeStr = `${hours}:${String(minutes).padStart(2, '0')}`
  return `${dateStr} ${timeStr} 更新，下一次自动发布：明日 08:00`
})

const poolStatus = computed(() => contentStore.poolStatus)
const meterPercent = computed(() => {
  if (!poolStatus.value) return 68
  const total = poolStatus.value.total || 30
  const approved = poolStatus.value.approved || 0
  return Math.round((approved / total) * 100)
})

onMounted(() => {
  contentStore.refreshStats()
})
</script>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: 248px minmax(0, 1fr);
  min-height: 100vh;
}

/* ---- Sidebar ---- */
.sidebar {
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  padding: 22px 18px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 48px;
}

.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  background: #edf6ef;
  display: grid;
  place-items: center;
  overflow: hidden;
  flex: 0 0 auto;
}

.brand-mark img {
  width: 36px;
  height: 36px;
  object-fit: contain;
}

.brand strong {
  display: block;
  font-size: 16px;
  line-height: 1.2;
}

.brand span {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--sidebar-faint);
}

.nav {
  display: grid;
  gap: 6px;
}

.nav-item {
  width: 100%;
  height: 42px;
  border-radius: 7px;
  color: var(--sidebar-muted);
  background: transparent;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 12px;
  text-align: left;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.15s;
}

.nav-item.active,
.nav-item:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, .1);
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
}

.sidebar-footer {
  margin-top: auto;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: 8px;
  background: rgba(255, 255, 255, .05);
}

.sidebar-footer p {
  margin: 0 0 10px;
  color: #c7d6d0;
  font-size: 13px;
  line-height: 1.5;
}

.mini-meter {
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
  background: rgba(255, 255, 255, .14);
}

.mini-meter span {
  display: block;
  height: 100%;
  background: #7bc7a8;
  border-radius: inherit;
  transition: width 0.5s ease;
}

/* ---- Main ---- */
.main {
  min-width: 0;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
}

.topbar {
  min-height: 72px;
  background: var(--panel);
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 14px 28px;
}

.page-title h1 {
  margin: 0;
  font-size: 22px;
  line-height: 1.25;
  font-weight: 760;
}

.page-title p {
  margin: 5px 0 0;
  color: var(--muted);
  font-size: 13px;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.content {
  min-height: 0;
  overflow: auto;
}

/* ---- Responsive ---- */
@media (max-width: 1180px) {
  .app-shell {
    grid-template-columns: 88px minmax(0, 1fr);
  }

  .brand {
    justify-content: center;
  }

  .brand div:not(.brand-mark),
  .nav-item span,
  .sidebar-footer {
    display: none;
  }

  .nav-item {
    justify-content: center;
    padding: 0;
  }
}

@media (max-width: 760px) {
  .app-shell {
    display: block;
  }

  .sidebar {
    position: sticky;
    top: 0;
    z-index: 8;
    min-height: auto;
    padding: 10px 12px;
    flex-direction: row;
    align-items: center;
  }

  .brand div:not(.brand-mark) {
    display: block;
  }

  .nav {
    grid-auto-flow: column;
    overflow: auto;
    flex: 1;
  }

  .nav-item {
    width: 42px;
  }

  .topbar {
    align-items: flex-start;
    flex-direction: column;
    padding: 16px;
  }

  .top-actions {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (max-width: 500px) {
  .page-title h1 {
    font-size: 19px;
  }
}
</style>
