<template>
  <div>
    <h2>Task Distribution</h2>
    
    <div style="display: flex; gap: 20px;">
        <!-- Left: Create Task Form -->
        <a-card title="Create New Task" style="flex: 1">
            <a-form layout="vertical" :model="formState" @finish="onFinish">
                <a-form-item label="Task Title" name="title" :rules="[{ required: true }]">
                    <a-input v-model:value="formState.title" placeholder="e.g. Submit Weekly Report" />
                </a-form-item>
                
                <a-form-item label="Task Content" name="content" :rules="[{ required: true }]">
                    <a-textarea v-model:value="formState.content" :rows="4" placeholder="Details..." />
                </a-form-item>
                
                <a-form-item label="Assign To" name="assignee_ids" :rules="[{ required: true, message: 'Select at least one user' }]">
                    <a-select
                        v-model:value="formState.assignee_ids"
                        mode="multiple"
                        placeholder="Select users"
                        :loading="usersLoading"
                        style="width: 100%"
                    >
                        <a-select-option v-for="user in users" :key="user.id" :value="user.id">
                            {{ user.display_name }} ({{ user.username }})
                        </a-select-option>
                    </a-select>
                    <div style="margin-top: 8px">
                        <a-button size="small" @click="selectAll">Select All</a-button>
                        <a-divider type="vertical" />
                        <a-button size="small" @click="formState.assignee_ids = []">Clear</a-button>
                    </div>
                </a-form-item>
                
                <a-form-item>
                    <a-button type="primary" html-type="submit" :loading="submitting">Distribute Task</a-button>
                </a-form-item>
            </a-form>
        </a-card>
        
        <!-- Right: Recent History (Placeholder / Future) -->
        <a-card title="Recent Distributions" style="flex: 1">
            <a-empty description="History not implemented in Phase 2" />
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
            assignee_ids: formState.assignee_ids
        });
        message.success(`Task distributed to ${formState.assignee_ids.length} users`);
        // Reset form
        formState.title = '';
        formState.content = '';
        formState.assignee_ids = [];
    } catch (e: any) {
        message.error("Failed to distribute task: " + (e.response?.data?.detail || e.message));
    } finally {
        submitting.value = false;
    }
}
</script>
