<template>
  <div class="login-container">
    <a-button 
        type="text" 
        shape="circle" 
        class="close-btn"
        @click="getCurrentWindow().close()"
    >
        <template #icon>✕</template>
    </a-button>
    <a-card title="内部任务系统" style="width: 300px">
      <a-form :model="formState" @finish="onFinish">
        <a-form-item
          name="username"
          :rules="[{ required: true, message: '请输入用户名!' }]"
        >
          <a-input v-model:value="formState.username" placeholder="用户名" />
        </a-form-item>

        <a-form-item
          name="password"
          :rules="[{ required: true, message: '请输入密码!' }]"
        >
          <a-input-password v-model:value="formState.password" placeholder="密码" />
        </a-form-item>

        <a-form-item>
          <a-button type="primary" html-type="submit" block :loading="loading">
            登录
          </a-button>
        </a-form-item>
      </a-form>
      <div v-if="error" class="error-msg">{{ error }}</div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { getCurrentWindow } from '@tauri-apps/api/window';

const authStore = useAuthStore();
const loading = ref(false);
const error = ref('');

const formState = reactive({
  username: '',
  password: '',
});

const onFinish = async (values: any) => {
  loading.value = true;
  error.value = '';
  try {
    await authStore.login(values.username, values.password);
  } catch (err: any) {
    console.error(err);
    error.value = "Login failed: " + (err.response?.data?.detail || err.message);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
  /* Allow dragging the window from background */
  -webkit-app-region: drag; 
  position: relative;
}
:deep(.ant-card) {
    -webkit-app-region: no-drag;
}
.error-msg {
    color: red;
    text-align: center;
    margin-top: 10px;
}
.close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    -webkit-app-region: no-drag;
    z-index: 1000;
}
</style>
