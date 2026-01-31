<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible>
      <div class="logo">DepApp Admin</div>
      <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline">
        <a-menu-item key="dashboard" @click="$router.push('/admin/dashboard')">
          <span>Overview</span>
        </a-menu-item>
        <a-menu-item key="users" @click="$router.push('/admin/users')">
          <span>User Management</span>
        </a-menu-item>
        <a-menu-item key="tasks" @click="$router.push('/admin/tasks-manage')">
          <span>Task Distribution</span>
        </a-menu-item>
        <a-menu-item key="logout" @click="handleLogout">
            <span style="color: #ff4d4f">Logout</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header style="background: #fff; padding: 0 16px">
        <span>Welcome, Administrator</span>
      </a-layout-header>
      <a-layout-content style="margin: 16px">
        <div :style="{ padding: '24px', background: '#fff', minHeight: '360px' }">
            <router-view></router-view>
        </div>
      </a-layout-content>
      <a-layout-footer style="text-align: center">
        Internal Task System ©2026
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const collapsed = ref(false);
const selectedKeys = ref<string[]>(['dashboard']);
const authStore = useAuthStore();
const router = useRouter();

function handleLogout() {
    authStore.logout();
    router.push('/login');
}
</script>

<style scoped>
.logo {
  height: 32px;
  background: rgba(255, 255, 255, 0.3);
  margin: 16px;
  text-align: center;
  line-height: 32px;
  color: white;
  font-weight: bold;
}
</style>
