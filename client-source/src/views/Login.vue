<template>
  <div class="login-container">
    <a-card title="Internal Task System" style="width: 300px">
      <a-form :model="formState" @finish="onFinish">
        <a-form-item
          name="username"
          :rules="[{ required: true, message: 'Please input your username!' }]"
        >
          <a-input v-model:value="formState.username" placeholder="Username" />
        </a-form-item>

        <a-form-item
          name="password"
          :rules="[{ required: true, message: 'Please input your password!' }]"
        >
          <a-input-password v-model:value="formState.password" placeholder="Password" />
        </a-form-item>

        <a-form-item>
          <a-button type="primary" html-type="submit" block :loading="loading">
            Log in
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
}
:deep(.ant-card) {
    -webkit-app-region: no-drag;
}
.error-msg {
    color: red;
    text-align: center;
    margin-top: 10px;
}
</style>
