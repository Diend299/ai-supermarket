<template>
  <div class="register-container">
    <div class="register-card">
      <h1 class="title">创建账号</h1>
      <p class="subtitle">加入AI Supermarket</p>
      
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            placeholder="请输入用户名"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="email">邮箱（选填）</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="请输入邮箱"
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            required
          />
        </div>
        
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      
      <div class="footer">
        <span>已有账号？</span>
        <router-link to="/login">立即登录</router-link>
      </div>
      
      <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/api/auth'

const router = useRouter()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})
const loading = ref(false)
const errorMsg = ref('')

const handleRegister = async () => {
  if (!form.value.username || !form.value.password) {
    errorMsg.value = '请填写完整信息'
    return
  }
  
  if (form.value.password !== form.value.confirmPassword) {
    errorMsg.value = '两次密码输入不一致'
    return
  }
  
  if (form.value.password.length < 6) {
    errorMsg.value = '密码长度至少为6位'
    return
  }
  
  loading.value = true
  errorMsg.value = ''
  
  try {
    const res = await register({
      username: form.value.username,
      email: form.value.email || undefined,
      password: form.value.password
    })
    
    if (res.code === 0) {
      router.push('/login')
    } else {
      errorMsg.value = res.msg
    }
  } catch (err: any) {
    errorMsg.value = err.response?.data?.msg || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  background: white;
  border-radius: 16px;
  padding: 48px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.title {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px;
  text-align: center;
}

.subtitle {
  font-size: 16px;
  color: #666;
  margin: 0 0 40px;
  text-align: center;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  padding: 14px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s;
  outline: none;
}

.form-group input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.submit-btn {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.footer {
  margin-top: 32px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  margin-left: 4px;
}

.footer a:hover {
  text-decoration: underline;
}

.error-msg {
  margin-top: 16px;
  padding: 12px;
  background: #fff0f0;
  color: #d32f2f;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
}
</style>
