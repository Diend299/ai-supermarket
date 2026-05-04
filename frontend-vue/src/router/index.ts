import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue')
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: '/copywriting',
        name: 'Copywriting',
        component: () => import('@/views/Copywriting.vue')
      },
      {
        path: '/avatar',
        name: 'Avatar',
        component: () => import('@/views/Avatar.vue')
      },
      {
        path: '/multimedia-workbench',
        name: 'MultimediaWorkbench',
        component: () => import('@/views/MultimediaWorkbench.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isLoggedIn()) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && userStore.isLoggedIn()) {
    next('/')
  } else {
    next()
  }
})

export default router
