<template>
  <div class="report-container">
    <div class="header">
      <a-button type="text" @click="$router.push('/tasks')">
        <template #icon>&lt;</template> Back
      </a-button>
      <span>Weekly Report</span>
    </div>

    <a-form layout="vertical" :model="formState" @finish="onFinish" class="report-form">
      <a-form-item label="Week Number">
        <a-input-number v-model:value="formState.week_num" style="width: 100%" />
      </a-form-item>

      <div class="scroll-area">
        <a-form-item label="Work Done" :rules="[{ required: true }]">
          <a-textarea v-model:value="formState.content_done" :rows="3" placeholder="What did you finish?" />
        </a-form-item>

        <a-form-item label="Next Week Plan" :rules="[{ required: true }]">
          <a-textarea v-model:value="formState.content_plan" :rows="3" placeholder="Plan for next week" />
        </a-form-item>

        <a-form-item label="Issues / Risks" :rules="[{ required: true }]">
          <a-textarea v-model:value="formState.content_issues" :rows="3" placeholder="Any blockers?" />
        </a-form-item>
      </div>

      <a-button type="primary" html-type="submit" block :loading="submitting">Submit Report</a-button>
    </a-form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import api from '../api/request';
import { useRouter } from 'vue-router';

// Helper to get current week number (ISO 8601ish)
function getWeekNumber(d: Date) {
    d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
    var yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    var weekNo = Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
    return parseInt(d.getUTCFullYear() + String(weekNo).padStart(2, '0'));
}

const router = useRouter();
const submitting = ref(false);
const formState = reactive({
    week_num: 202601,
    content_done: '',
    content_plan: '',
    content_issues: ''
});

onMounted(() => {
    formState.week_num = getWeekNumber(new Date());
});

async function onFinish() {
    submitting.value = true;
    try {
        await api.post('/reports', { ...formState });
        message.success('Report submitted successfully');
        router.push('/tasks');
    } catch (e: any) {
        message.error("Failed to submit: " + (e.response?.data?.detail || e.message));
    } finally {
        submitting.value = false;
    }
}
</script>

<style scoped>
.report-container {
    padding: 10px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #fff;
}
.header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    font-weight: bold;
    -webkit-app-region: drag;
}
.report-form {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
}
.scroll-area {
    flex: 1;
    overflow-y: auto;
    padding-right: 5px; /* space for scrollbar */
    margin-bottom: 10px;
}
</style>
