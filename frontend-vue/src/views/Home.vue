<template>
  <div class="app-container">
    <aside class="sidebar">
      <div class="logo-section">
        <div class="logo">
          <img src="@/assets/logo.png" alt="AI超市平台" class="logo-img" />
          <span class="logo-text">AI超市平台</span>
        </div>
        <p class="logo-subtitle">多Agent协同式AI企业运营平台</p>
      </div>

      <nav class="nav-menu">
        <div class="nav-group">
          <h3 class="nav-group-title">工作台</h3>
          <div class="nav-items">
            <button
              v-for="item in workbenchItems"
              :key="item.id"
              @click="navigateTo(item)"
              :class="['nav-item', { active: activeItem === item.id }]"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              <span class="nav-text">{{ item.name }}</span>
            </button>
          </div>
        </div>

        <div class="nav-group">
          <h3 class="nav-group-title">核心模块</h3>
          <div class="nav-items">
            <button
              v-for="item in coreModules"
              :key="item.id"
              @click="navigateTo(item)"
              :class="['nav-item', { active: activeItem === item.id }]"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              <span class="nav-text">{{ item.name }}</span>
            </button>
          </div>
        </div>

        <div class="nav-group">
          <h3 class="nav-group-title">管理中心</h3>
          <div class="nav-items">
            <button
              v-for="item in managementItems"
              :key="item.id"
              @click="navigateTo(item)"
              :class="['nav-item', { active: activeItem === item.id }]"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              <span class="nav-text">{{ item.name }}</span>
            </button>
          </div>
        </div>
      </nav>

      <div class="user-footer">
        <div class="user-info">
          <span class="user-avatar">👤</span>
          <div class="user-details">
            <span class="user-name">{{ userStore.username }}</span>
            <span class="user-role">企业管理员</span>
          </div>
        </div>
        <button @click="handleLogout" class="logout-btn">
          <span>退出登录</span>
        </button>
      </div>
    </aside>

    <main class="main-content">
      <header class="top-header">
        <div class="header-left">
          <h2 class="page-title">{{ currentPageTitle }}</h2>
          <p class="page-subtitle">{{ currentPageSubtitle }}</p>
        </div>
        <div class="header-right">
          <div class="header-actions">
            <button class="action-btn">
              <span class="action-icon">🔔</span>
              <span class="badge">3</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">⚙️</span>
            </button>
          </div>
        </div>
      </header>

      <div class="content-area">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeItem = ref<string>(route.name as string || 'dashboard')

watch(() => route.name, (name) => {
  if (name) {
    activeItem.value = name as string
  }
})

const navigateTo = (item: { id: string; route?: string }) => {
  if (item.route) {
    activeItem.value = item.id
    router.push(item.route)
  }
}

const workbenchItems = [
  { id: 'dashboard', name: '今日任务', icon: '📋', route: '/' },
  { id: 'reports', name: '数据看板', icon: '📊' },
  { id: 'multimedia', name: '多媒体工作台', icon: '🎛️', route: '/multimedia-workbench' },
  { id: 'messages', name: '消息中心', icon: '💬' }
]

const coreModules = [
  { id: 'marketing', name: '营销智脑', icon: '🎯' },
  { id: 'operations', name: '运营规划', icon: '📈' },
  { id: 'creative', name: '创意部门', icon: '🎨' },
  { id: 'production', name: '生产部门', icon: '🏭' },
  { id: 'customer', name: '获客部门', icon: '👥' },
  { id: 'sales', name: '成交部门', icon: '💰' },
  { id: 'growth', name: '增长部门', icon: '🌱' },
  { id: 'support', name: '支持部门', icon: '🛠️' },
  { id: 'avatar', name: '数字人', icon: '👤', route: '/avatar' }
]

const managementItems = [
  { id: 'assets', name: '资产管理', icon: '📦' },
  { id: 'finance', name: '财务管理', icon: '💳' },
  { id: 'apps', name: '应用中心', icon: '📱' },
  { id: 'knowledge', name: '智能知识库', icon: '📚' },
  { id: 'enterprise', name: '企业设置', icon: '🏢' },
  { id: 'system', name: '系统管理', icon: '⚙️' }
]

const pageMeta: Record<string, { title: string; subtitle: string }> = {
  dashboard: { title: '工作台', subtitle: '让AI像超市一样触手可及' },
  Copywriting: { title: 'AI文案创作', subtitle: '输入需求，AI自动生成优质营销文案' },
  Avatar: { title: 'AI数字人', subtitle: '上传照片，输入文案，AI生成数字人视频' },
  marketing: { title: '营销智脑', subtitle: '智能营销分析与决策支持' },
  operations: { title: '运营规划', subtitle: '全方位运营规划与执行' },
  creative: { title: '创意部门', subtitle: '激发创意灵感，提升内容质量' },
  production: { title: '生产部门', subtitle: '高效内容生产与管理' },
  customer: { title: '获客部门', subtitle: '精准获客与客户管理' },
  sales: { title: '成交部门', subtitle: '智能成交转化与跟进' },
  growth: { title: '增长部门', subtitle: '持续增长策略与优化' }
}

const currentPageTitle = computed(() => {
  return pageMeta[activeItem.value]?.title || '工作台'
})

const currentPageSubtitle = computed(() => {
  return pageMeta[activeItem.value]?.subtitle || '多Agent协同式AI企业运营平台'
})

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
  width: 100%;
}

.sidebar {
  width: 280px;
  background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  overflow-y: auto;
  z-index: 100;
}

.logo-section {
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.logo-img {
  width: 40px;
  height: 40px;
  object-fit: contain;
  filter: brightness(0) invert(1);
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
}

.logo-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.nav-menu {
  flex: 1;
  padding: 16px;
}

.nav-group {
  margin-bottom: 24px;
}

.nav-group-title {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0 0 12px;
  padding: 0 8px;
}

.nav-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-item.active {
  background: rgba(139, 92, 246, 0.3);
  color: white;
}

.nav-icon {
  font-size: 18px;
}

.nav-text {
  flex: 1;
}

.user-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
}

.user-role {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.logout-btn {
  width: 100%;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.main-content {
  flex: 1;
  margin-left: 280px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.top-header {
  background: white;
  padding: 20px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-left {
  display: flex;
  flex-direction: column;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1e1b4b;
}

.page-subtitle {
  margin: 4px 0 0;
  font-size: 14px;
  color: #666;
}

.header-right {
  display: flex;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 16px;
}

.action-btn {
  position: relative;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #f5f7fa;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.action-btn:hover {
  background: #e8eaf0;
}

.action-icon {
  font-size: 20px;
}

.badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #ef4444;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
}

.content-area {
  flex: 1;
  padding: 24px 24px;
  overflow: visible;
  width: 100%;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .content-row {
    grid-template-columns: 1fr;
  }

  .quick-actions {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    position: relative;
  }

  .main-content {
    margin-left: 0;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
