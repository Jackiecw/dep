<template>
  <div>
    <h2>任务分发</h2>
    
    <div style="display: flex; gap: 20px;">
        <!-- Left: Create Task Form -->
        <a-card title="创建新任务" style="flex: 1">
            <a-form layout="vertical" :model="formState" @finish="onFinish">
                <a-form-item label="任务标题" name="title" :rules="[{ required: true, message: '请输入任务标题' }]">
                    <a-input v-model:value="formState.title" placeholder="例如: 提交周报" />
                </a-form-item>
                
                <a-form-item label="任务内容" name="content" :rules="[{ required: true }]">
                    <a-textarea v-model:value="formState.content" :rows="4" placeholder="任务详情..." />
                </a-form-item>

                <a-form-item label="截止时间" name="deadline">
                    <a-date-picker 
                        v-model:value="formState.deadline" 
                        show-time 
                        format="YYYY-MM-DD HH:mm" 
                        placeholder="选择截止时间 (可选)" 
                        style="width: 100%"
                    />
                </a-form-item>
                
                <a-form-item label="指派给" name="assignee_ids" :rules="[{ required: true, message: '请至少选择一个用户' }]">
                    <a-select
                        v-model:value="formState.assignee_ids"
                        mode="multiple"
                        placeholder="选择用户"
                        :loading="usersLoading"
                        style="width: 100%"
                    >
                        <a-select-option v-for="user in users" :key="user.id" :value="user.id">
                            {{ user.display_name }} ({{ user.username }})
                        </a-select-option>
                    </a-select>
                    <div style="margin-top: 8px">
                        <a-button size="small" @click="selectAll">全选</a-button>
                        <a-divider type="vertical" />
                        <a-button size="small" @click="formState.assignee_ids = []">清空</a-button>
                    </div>
                </a-form-item>
                
                <a-form-item>
                    <a-button type="primary" html-type="submit" :loading="submitting">分发任务</a-button>
                </a-form-item>
            </a-form>
        </a-card>
        
        <!-- Right: Recent History -->
        <a-card title="最近分发记录" style="flex: 1">
            <a-empty description="暂无记录" />
        </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import api from '../../api/request';

interface User {
    id: number;
    username: string;
    display_name: string;
}

const users = ref<User[]>([]);
const usersLoading = ref(false);
const submitting = ref(false);

const formState = reactive({
    title: '',
    content: '',
    deadline: undefined,
    assignee_ids: [] as number[]
});

onMounted(() => {
    fetchUsers();
});

async function fetchUsers() {
    usersLoading.value = true;
    try {
        const res = await api.get('/users');
        users.value = res.data;
    } catch (e) {
        message.error("Failed to load users");
    } finally {
        usersLoading.value = false;
    }
}

function selectAll() {
    formState.assignee_ids = users.value.map(u => u.id);
}

async function onFinish() {
    submitting.value = true;
    try {
        await api.post('/tasks', {
            title: formState.title,
            content: formState.content,
            deadline: formState.deadline ? (formState.deadline as any).format('YYYY-MM-DD HH:mm:ss') : null,
            assignee_ids: formState.assignee_ids
        });
        message.success(`任务已分发给 ${formState.assignee_ids.length} 名用户`);
        // Reset form
        formState.title = '';
        formState.content = '';
        formState.deadline = undefined;
        formState.assignee_ids = [];
    } catch (e: any) {
        message.error("分发任务失败: " + (e.response?.data?.detail || e.message));
    } finally {
        submitting.value = false;
    }
}
</script>
