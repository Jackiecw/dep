<template>
  <div class="task-list-container">
    <div class="header">
        <h3 style="margin: 0">My Tasks</h3>
        <div>
            <a-button type="link" size="small" @click="$router.push('/reports')">Week Report</a-button>
            <a-button type="text" size="small" @click="authStore.logout">Logout</a-button>
        </div>
    </div>
    
    <div class="task-items">
        <a-empty v-if="tasks.length === 0" description="No pending tasks" />
        
        <div v-for="task in tasks" :key="task.id" class="task-item">
            <a-checkbox 
                :checked="task.status === 'done'" 
                @change="(e: any) => onCheck(task, e.target.checked)"
            >
                <span :class="{ done: task.status === 'done' }">{{ task.title }}</span>
            </a-checkbox>
            <div class="task-meta">{{ formatDate(task.created_at) }}</div>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import api from '../api/request';

interface Task {
    id: number;
    title: string;
    content: string;
    status: string; // 'pending' | 'done'
    created_at: string;
}

const authStore = useAuthStore();
const tasks = ref<Task[]>([]);

onMounted(() => {
    fetchTasks();
    // Poll every 30 seconds
    setInterval(fetchTasks, 30000);
});

async function fetchTasks() {
    try {
        const res = await api.get<Task[]>('/tasks');
        tasks.value = res.data;
    } catch (e) {
        console.error(e);
    }
}

async function onCheck(task: Task, checked: boolean) {
    if(!checked) return; // Only support checking done for now
    
    try {
        // Optimistic update
        task.status = 'done';
        await api.put(`/tasks/${task.id}`, { status: 'done' });
    } catch (e) {
        // Revert on fail
        task.status = 'pending';
        console.error(e);
    }
}

function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleString();
}
</script>

<style scoped>
.task-list-container {
    padding: 10px;
    height: 100vh;
    background: rgba(255, 255, 255, 0.9); /* Semi-transparent */
    display: flex;
    flex-direction: column;
}
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    -webkit-app-region: drag; /* Drag by header */
    cursor: move;
}
.task-items {
    flex: 1;
    overflow-y: auto;
}
.task-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}
.task-meta {
    font-size: 0.8em;
    color: #999;
}
.done {
    text-decoration: line-through;
    color: #ccc;
}
</style>
