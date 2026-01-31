<template>
  <div class="report-container">
    <div class="header" style="-webkit-app-region: drag">
      <span class="page-title">周报提交</span>
      <span class="sub-title">Weekly Report Submission</span>
    </div>

    <div class="content-wrapper">
        <a-card class="report-card" :bordered="false">
            <template #title>
                <div class="card-title">
                    <span>第 {{ formState.week_num }} 周工作汇报</span>
                    <span class="date-range">{{ weekRange }}</span>
                </div>
            </template>
            
            <a-form layout="vertical" :model="formState" @finish="onFinish" class="report-form">
            
            <div class="form-section">
                <!-- Week Num (Hidden or Readonly if auto-calculated usually, but kept editable as per original) -->
                <a-form-item label="周次 (YYYYWW)">
                    <a-input-number v-model:value="formState.week_num" style="width: 200px" />
                </a-form-item>

                <!-- Toolbar for Content -->
                 <div class="toolbar-container">
                    <span class="toolbar-label">快速工具:</span>
                    <a-space>
                        <a-button size="small" @click="insertText('• ')">Python list (•)</a-button>
                        <a-button size="small" @click="insertText('【', '】')">【标题】</a-button>
                        <a-button size="small" @click="insertText('- ')">列表 (-)</a-button>
                        <a-button size="small" @click="insertText('\n----------------\n')">分割线</a-button>
                    </a-space>
                 </div>

                <a-form-item label="本周工作内容" :rules="[{ required: true, message: '请填写本周工作内容' }]">
                    <a-textarea 
                        ref="contentDoneRef"
                        id="content_done"
                        v-model:value="formState.content_done" 
                        :rows="6" 
                        placeholder="1. 完成了..." 
                        @focus="activeField = 'content_done'"
                    />
                </a-form-item>

                <a-form-item label="下周工作计划" :rules="[{ required: true, message: '请填写下周计划' }]">
                    <a-textarea 
                        ref="contentPlanRef"
                        id="content_plan"
                        v-model:value="formState.content_plan" 
                        :rows="6" 
                        placeholder="1. 计划..." 
                        @focus="activeField = 'content_plan'"
                    />
                </a-form-item>

                <a-form-item label="存在的问题与风险" :rules="[{ required: true, message: '请填写问题或风险' }]">
                    <a-textarea 
                        ref="contentIssuesRef"
                        id="content_issues"
                        v-model:value="formState.content_issues" 
                        :rows="4" 
                        placeholder="无" 
                         @focus="activeField = 'content_issues'"
                    />
                </a-form-item>
            </div>

            <div class="form-actions">
                <a-button type="primary" size="large" html-type="submit" :loading="submitting">提交周报</a-button>
                <a-button size="large" @click="getCurrentWindow().close()" style="margin-left: 10px">取消</a-button>
            </div>
            </a-form>
        </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue';
import { message } from 'ant-design-vue';
import api from '../api/request';
import { getCurrentWindow } from '@tauri-apps/api/window';

// Helper to get current week number (ISO 8601ish)
function getWeekNumber(d: Date) {
    d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
    var yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    var weekNo = Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
    return parseInt(d.getUTCFullYear() + String(weekNo).padStart(2, '0'));
}

const submitting = ref(false);
const activeField = ref('content_done');
const formState = reactive({
    week_num: 202601,
    content_done: '',
    content_plan: '',
    content_issues: ''
});

onMounted(() => {
    formState.week_num = getWeekNumber(new Date());
});

const weekRange = computed(() => {
    // Placeholder for actual date range calculation logic if desired
    return `${new Date().toLocaleDateString()} - ...`;
});

function insertText(prefix: string, suffix: string = '') {
    // Simple append if no advanced selection logic (for MVP)
    // For a better experience, we can try to insert at cursor position if we had ref access to the native element easier
    // But V-Model binding makes simple append safest without complex DOM manipulation
    // Let's try to do a bit better by appending to end for now as "Insert" usually implies at cursor but simple append is robust
    
    // Actually, let's try to find the active element
    const el = document.getElementById(activeField.value) as HTMLTextAreaElement;
    if (el) {
        const start = el.selectionStart;
        const end = el.selectionEnd;
        const text = el.value;
        const before = text.substring(0, start);
        const after = text.substring(end, text.length);
        
        // Update model
        const newVal = before + prefix + suffix + after;
        
        // Need to update formState to react
        if (activeField.value === 'content_done') formState.content_done = newVal;
        if (activeField.value === 'content_plan') formState.content_plan = newVal;
        if (activeField.value === 'content_issues') formState.content_issues = newVal;

        // Restore cursor (approximate, next tick)
        setTimeout(() => {
            el.focus();
            el.setSelectionRange(start + prefix.length, start + prefix.length);
        }, 0);
    } else {
         // Fallback
         if (activeField.value === 'content_done') formState.content_done += prefix + suffix;
         // ... others
    }
}

async function onFinish() {
    submitting.value = true;
    try {
        await api.post('/reports', { ...formState });
        message.success('周报提交成功');
        setTimeout(() => {
            getCurrentWindow().close();
        }, 1500);
    } catch (e: any) {
        message.error("提交失败: " + (e.response?.data?.detail || e.message));
    } finally {
        submitting.value = false;
    }
}
</script>

<style scoped>
.report-container {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #f0f2f5; /* Soft gray background */
}
.header {
    height: 50px;
    padding: 0 20px;
    display: flex;
    align-items: center;
    background: #001529;
    color: white;
    justify-content: space-between;
}
.page-title {
    font-size: 16px;
    font-weight: bold;
}
.sub-title {
    font-size: 12px;
    opacity: 0.7;
}

.content-wrapper {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    justify-content: center;
}

.report-card {
    width: 100%;
    max-width: 800px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    border-radius: 8px;
}

.card-title {
    display: flex;
    flex-direction: column;
}
.date-range {
    font-size: 12px;
    color: #999;
    font-weight: normal;
}

.toolbar-container {
    background: #fafafa;
    padding: 8px;
    border-radius: 4px;
    margin-bottom: 16px;
    border: 1px solid #f0f0f0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.toolbar-label {
    font-size: 12px;
    color: #888;
}

.form-actions {
    margin-top: 24px;
    text-align: center;
    padding-top: 20px;
    border-top: 1px solid #f0f0f0;
}
</style>
