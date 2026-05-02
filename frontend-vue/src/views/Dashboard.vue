<template>
  <div>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon bg-purple">📊</div>
        <div class="stat-content">
          <span class="stat-value">128</span>
          <span class="stat-label">今日任务</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon bg-blue">💰</div>
        <div class="stat-content">
          <span class="stat-value">¥85,620</span>
          <span class="stat-label">本月营收</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon bg-green">📈</div>
        <div class="stat-content">
          <span class="stat-value">23.5%</span>
          <span class="stat-label">增长率</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon bg-orange">👥</div>
        <div class="stat-content">
          <span class="stat-value">1,256</span>
          <span class="stat-label">活跃用户</span>
        </div>
      </div>
    </div>
    
    <div class="content-section">
      <div class="section-header">
        <h3>快捷操作</h3>
        <button class="view-all">查看全部</button>
      </div>
      <div class="quick-actions">
        <button 
          v-for="action in quickActions" 
          :key="action.id"
          class="quick-action-btn"
          @click="goToPage(action.route)"
        >
          <span class="quick-icon">{{ action.icon }}</span>
          <span class="quick-label">{{ action.label }}</span>
        </button>
      </div>
    </div>
    
    <div class="content-row">
      <div class="content-card">
        <div class="card-header">
          <h3>今日任务</h3>
          <span class="card-badge">{{ todayTasks.length }} 项</span>
        </div>
        <div class="task-list">
          <div 
            v-for="task in todayTasks" 
            :key="task.id"
            class="task-item"
          >
            <div class="task-checkbox">
              <input type="checkbox" :checked="task.completed" />
            </div>
            <div class="task-info">
              <span class="task-title">{{ task.title }}</span>
              <span class="task-time">{{ task.time }}</span>
            </div>
            <span :class="['task-tag', task.tagClass]">{{ task.tag }}</span>
          </div>
        </div>
      </div>
      
      <div class="content-card">
        <div class="card-header">
          <h3>数据概览</h3>
          <select class="period-select">
            <option>本周</option>
            <option>本月</option>
            <option>本季度</option>
          </select>
        </div>
        <div class="chart-placeholder">
          <div class="chart-bars">
            <div class="bar-container" v-for="(bar, index) in chartData" :key="index">
              <div class="bar" :style="{ height: bar.value + '%' }"></div>
              <span class="bar-label">{{ bar.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="content-row">
      <div class="content-card">
        <div class="card-header">
          <h3>最近动态</h3>
        </div>
        <div class="activity-list">
          <div 
            v-for="activity in recentActivities" 
            :key="activity.id"
            class="activity-item"
          >
            <span class="activity-icon">{{ activity.icon }}</span>
            <div class="activity-content">
              <span class="activity-text">{{ activity.text }}</span>
              <span class="activity-time">{{ activity.time }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="content-card">
        <div class="card-header">
          <h3>系统通知</h3>
          <span class="card-badge">新</span>
        </div>
        <div class="notification-list">
          <div 
            v-for="notification in notifications" 
            :key="notification.id"
            :class="['notification-item', { unread: notification.unread }]"
          >
            <span :class="['notification-icon', notification.type]">{{ notification.icon }}</span>
            <div class="notification-content">
              <span class="notification-title">{{ notification.title }}</span>
              <span class="notification-time">{{ notification.time }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goToPage = (page: string) => {
  if (page) {
    router.push(page)
  }
}

const quickActions = [
  { id: 'video', icon: '🎬', label: '视频生成', route: '' },
  { id: 'avatar', icon: '👤', label: '数字人', route: '/avatar' },
  { id: 'text', icon: '📝', label: '文案创作', route: '/copywriting' },
  { id: 'image', icon: '🖼️', label: '图片生成', route: '' },
  { id: 'analysis', icon: '📊', label: '数据分析', route: '' },
  { id: 'plan', icon: '📋', label: '计划制定', route: '' }
]

const todayTasks = [
  { id: 1, title: '完成营销周报', time: '09:00', tag: '营销', tagClass: 'tag-marketing', completed: false },
  { id: 2, title: '审核内容发布', time: '10:30', tag: '内容', tagClass: 'tag-content', completed: false },
  { id: 3, title: '客户跟进会议', time: '14:00', tag: '客户', tagClass: 'tag-customer', completed: true },
  { id: 4, title: '数据分析报告', time: '16:00', tag: '分析', tagClass: 'tag-analysis', completed: false },
  { id: 5, title: '团队周会', time: '17:30', tag: '团队', tagClass: 'tag-team', completed: false }
]

const chartData = [
  { label: '周一', value: 45 },
  { label: '周二', value: 68 },
  { label: '周三', value: 52 },
  { label: '周四', value: 85 },
  { label: '周五', value: 72 },
  { label: '周六', value: 35 },
  { label: '周日', value: 28 }
]

const recentActivities = [
  { id: 1, icon: '✅', text: '营销周报已生成', time: '5分钟前' },
  { id: 2, icon: '📤', text: '视频生成任务已完成', time: '15分钟前' },
  { id: 3, icon: '🔔', text: '新客户咨询已接收', time: '30分钟前' },
  { id: 4, icon: '📊', text: '数据分析报告已更新', time: '1小时前' },
  { id: 5, icon: '👥', text: '团队协作任务已分配', time: '2小时前' }
]

const notifications = [
  { id: 1, icon: '🔔', title: '系统更新通知', time: '刚刚', type: 'info', unread: true },
  { id: 2, icon: '⚠️', title: '任务即将到期提醒', time: '10分钟前', type: 'warning', unread: true },
  { id: 3, icon: '🎉', title: '营销活动效果显著', time: '1小时前', type: 'success', unread: false },
  { id: 4, icon: '💬', title: '新消息通知', time: '2小时前', type: 'info', unread: false }
]
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.bg-purple {
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
}

.stat-icon.bg-blue {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

.stat-icon.bg-green {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.stat-icon.bg-orange {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e1b4b;
}

.stat-label {
  font-size: 13px;
  color: #666;
}

.content-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e1b4b;
}

.view-all {
  color: #8b5cf6;
  font-size: 14px;
  font-weight: 500;
  background: none;
  border: none;
  cursor: pointer;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.quick-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: #f8fafc;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-action-btn:hover {
  background: #e8eaf0;
  transform: translateY(-2px);
}

.quick-icon {
  font-size: 32px;
}

.quick-label {
  font-size: 13px;
  color: #374151;
  font-weight: 500;
}

.content-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.content-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e1b4b;
}

.card-badge {
  background: #8b5cf6;
  color: white;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
}

.period-select {
  padding: 6px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 10px;
}

.task-checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.task-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-title {
  font-size: 14px;
  color: #374151;
}

.task-time {
  font-size: 12px;
  color: #9ca3af;
}

.task-tag {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 8px;
  font-weight: 500;
}

.task-tag.tag-marketing {
  background: #fef3c7;
  color: #d97706;
}

.task-tag.tag-content {
  background: #dbeafe;
  color: #2563eb;
}

.task-tag.tag-customer {
  background: #d1fae5;
  color: #059669;
}

.task-tag.tag-analysis {
  background: #ede9fe;
  color: #7c3aed;
}

.task-tag.tag-team {
  background: #fce7f3;
  color: #db2777;
}

.chart-placeholder {
  height: 200px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 20px 0;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 24px;
  height: 100%;
}

.bar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  height: 100%;
}

.bar {
  width: 40px;
  background: linear-gradient(180deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 8px 8px 0 0;
  transition: height 0.5s ease;
}

.bar-label {
  font-size: 12px;
  color: #6b7280;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.activity-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.activity-text {
  font-size: 14px;
  color: #374151;
}

.activity-time {
  font-size: 12px;
  color: #9ca3af;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  background: #f9fafb;
}

.notification-item.unread {
  background: #f5f3ff;
  border-left: 3px solid #8b5cf6;
}

.notification-icon {
  font-size: 20px;
}

.notification-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.notification-title {
  font-size: 14px;
  color: #374151;
}

.notification-time {
  font-size: 12px;
  color: #9ca3af;
}
</style>
