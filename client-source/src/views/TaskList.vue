<template>
  <div class="task-list-container" :class="{ 'pinned': settingsStore.isPinned }" :style="{ opacity: settingsStore.opacity / 100 }">
    <div class="header">
        <div class="title-area">
            <h3 style="margin: 0; font-weight: 600; color: #333;">任务列表</h3>
            <span class="date-badge">{{ new Date().toLocaleDateString() }}</span>
        </div>
        <div class="window-controls" style="-webkit-app-region: no-drag; z-index: 99999; position: relative;">
            <!-- Week Report Button: Opens new window -->
            <a-tooltip title="提交周报 (新窗口)">
                <a-button type="text" size="small" @click="openReportWindow">📅</a-button>
            </a-tooltip>
            <a-tooltip :title="settingsStore.isPinned ? '取消固定' : '固定窗口'">
                <a-button type="text" size="small" :class="{ active: settingsStore.isPinned }" @click="settingsStore.setPinned(!settingsStore.isPinned)">
                   <span v-if="settingsStore.isPinned">📌</span>
                   <span v-else>📍</span>
                </a-button>
            </a-tooltip>
            <a-button type="text" size="small" @click="settingsVisible = true">⚙️</a-button>
            <div class="sys-ctrls" style="-webkit-app-region: no-drag; z-index: 99999;">
                <a-button type="text" size="small" @click.stop="minimizeWindow" style="-webkit-app-region: no-drag; cursor: pointer;">_</a-button>
                <a-button type="text" size="small" danger @click.stop="closeWindow" style="-webkit-app-region: no-drag; cursor: pointer;">✕</a-button>
            </div>
        </div>
    </div>
    
    <div class="task-items custom-scroll">
        <a-empty v-if="tasks.length === 0" description="暂无待办任务" />
        
        <div 
            v-for="task in tasks" 
            :key="task.id" 
            class="task-card" 
            :style="{ background: getTaskColor(task) }"
            :class="{ 'urgent-task': isUrgent(task) }"
        >
            <div class="card-content">
                <div class="card-header">
                    <span class="task-title">{{ task.title }}</span>
                    <!-- Display Deadline if available, else Created At -->
                    <span v-if="task.deadline" class="time-tag deadline-tag">
                        截止: {{ formatTime(task.deadline) }}
                    </span>
                    <span v-else class="time-tag">
                        {{ formatTime(task.created_at) }}
                    </span>
                </div>
                <div class="card-desc" :title="task.content">{{ task.content }}</div>
            </div>
            <div class="card-actions">
                <a-popconfirm
                    title="确认已完成?"
                    ok-text="是"
                    cancel-text="否"
                    @confirm="onCheck(task)"
                >
                    <a-button type="primary" shape="circle" size="small" class="done-btn">✓</a-button>
                </a-popconfirm>
            </div>
        </div>
    </div>

    <!-- Settings Modal -->
    <a-modal v-model:open="settingsVisible" title="组件设置" :footer="null" :width="300">
        <div class="setting-item">
            <span>开机自启</span>
            <a-switch :checked="settingsStore.autoStart" @change="(val: boolean) => settingsStore.toggleAutoStart(val)" />
        </div>
        <div class="setting-item">
            <span>透明度</span>
            <a-slider v-model:value="computedOpacity" :min="20" :max="100" style="width: 120px" />
        </div>
        <div class="setting-item">
            <span>关闭按钮行为</span>
            <a-radio-group :value="settingsStore.closeBehavior" @update:value="(val: any) => settingsStore.setCloseBehavior(val)">
                <a-radio-button value="minimize">隐藏</a-radio-button>
                <a-radio-button value="quit">退出</a-radio-button>
            </a-radio-group>
        </div>
        <a-divider />
        <div class="setting-item" style="justify-content: flex-end">
            <a-button type="link" size="small" @click="authStore.logout">退出登录</a-button>
        </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useSettingsStore } from '../stores/settings';
import api from '../api/request';
import { getCurrentWindow, currentMonitor, PhysicalPosition } from '@tauri-apps/api/window';
import { WebviewWindow } from '@tauri-apps/api/webviewWindow';

interface Task {
    id: number;
    title: string;
    content: string;
    status: string;
    created_at: string;
    deadline?: string;
}

const authStore = useAuthStore();
const settingsStore = useSettingsStore();
const tasks = ref<Task[]>([]);
const settingsVisible = ref(false);

const computedOpacity = computed({
    get: () => settingsStore.opacity,
    set: (val) => settingsStore.setOpacity(val)
});

// Pastel colors
const cardColors = [
    '#fff0f6', '#e6f7ff', '#f6ffed', '#fff7e6', '#f9f0ff', '#fcffe6'
];

function getTaskColor(task: Task) {
    if (isUrgent(task)) return '#fff1f0'; // Reddish for urgent
    return cardColors[task.id % cardColors.length];
}

function isUrgent(task: Task) {
    if (!task.deadline) return false;
    const now = new Date();
    const deadline = new Date(task.deadline);
    const diffHours = (deadline.getTime() - now.getTime()) / (1000 * 60 * 60);
    return diffHours > 0 && diffHours < 4;
}

onMounted(async () => {
    fetchTasks();
    setInterval(fetchTasks, 30000);
    
    // Set initial position to Top-Right if not pinned
    if (!settingsStore.isPinned) {
        moveWindowToTopRight();
    }
});

async function moveWindowToTopRight() {
    try {
        const monitor = await currentMonitor();
        if (monitor) {
            const screenWidth = monitor.size.width;
            const windowWidth = 320; // Approx widget width
            const x = screenWidth - windowWidth - 20; // 20px padding
            const y = 20; // 20px padding
            await getCurrentWindow().setPosition(new PhysicalPosition(x, y));
        }
    } catch (e) {
        console.error("Failed to set window position", e);
    }
}

async function openReportWindow() {
    // Open new webview window for reports
    const webview = new WebviewWindow('report-window', {
        url: '/#/reports', // Use hash routing path
        title: 'Weekly Report',
        width: 1000,
        height: 800,
        center: true,
        resizable: true,
        decorations: true, // Standard window
        skipTaskbar: false // Show in taskbar
    });
    webview.once('tauri://created', function () {
        // webview window successfully created
    });
    webview.once('tauri://error', function (e) {
        // an error happened creating the webview window
        console.error(e);
    });
}

async function fetchTasks() {
    try {
        const res = await api.get<Task[]>('/tasks');
        tasks.value = res.data.filter(t => t.status !== 'done');
    } catch (e) {
        console.error(e);
    }
}

async function onCheck(task: Task) {
    try {
        tasks.value = tasks.value.filter(t => t.id !== task.id);
        await api.put(`/tasks/${task.id}`, { status: 'done' });
    } catch (e) {
        console.error(e);
        fetchTasks();
    }
}

function formatTime(dateStr: string) {
    const date = new Date(dateStr);
    const now = new Date();
    // If today, show time. Else show Date + Time
    const isToday = date.getDate() === now.getDate() && date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
    
    if (isToday) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function minimizeWindow() {
    getCurrentWindow().minimize();
}

function closeWindow() {
    getCurrentWindow().close();
}
</script>

<style scoped>
.task-list-container {
    padding: 12px;
    height: 100vh;
    background: #fdfdfd; 
    display: flex;
    flex-direction: column;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    overflow: hidden;
    border: 1px solid rgba(0,0,0,0.06);
    transition: all 0.3s ease;
}

/* Header */
.header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding-bottom: 12px;
    -webkit-app-region: drag; 
    cursor: move;
}
.pinned .header {
    -webkit-app-region: no-drag; 
    cursor: default;
}
/* ... existing styles ... */
/* Urgent Task */
.urgent-task {
    border: 1px solid #ffccc7 !important;
    animation: pulse-border 2s infinite;
}
@keyframes pulse-border {
    0% { box-shadow: 0 0 0 0 rgba(255, 77, 79, 0.4); }
    70% { box-shadow: 0 0 0 6px rgba(255, 77, 79, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 77, 79, 0); }
}
.deadline-tag {
    color: #ff4d4f;
    font-weight: 600;
}
</style>

<style scoped>
.task-list-container {
    padding: 12px;
    height: 100vh;
    background: #fdfdfd; 
    display: flex;
    flex-direction: column;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    overflow: hidden;
    border: 1px solid rgba(0,0,0,0.06);
    transition: all 0.3s ease;
}

/* Header */
.header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding-bottom: 12px;
    -webkit-app-region: drag; 
    cursor: move;
}
.pinned .header {
    -webkit-app-region: no-drag; 
    cursor: default;
}
.title-area {
    display: flex;
    flex-direction: column;
}
.date-badge {
    font-size: 0.75em;
    color: #888;
    margin-top: 2px;
}
.window-controls {
    display: flex;
    gap: 4px;
    -webkit-app-region: no-drag; /* CRITICAL FIX: Ensure controls are not draggable */
}
.sys-ctrls {
    display: flex;
    gap: 0;
    margin-left: 4px;
}
.window-controls button {
    color: #666;
}
.window-controls button:hover {
    background: rgba(0,0,0,0.05);
    color: #333;
}
.window-controls .active {
    color: #1890ff;
    background: rgba(24, 144, 255, 0.1);
}

/* Card List */
.task-items {
    flex: 1;
    overflow-y: auto;
    padding-right: 4px; 
}
.custom-scroll::-webkit-scrollbar {
    width: 4px;
}
.custom-scroll::-webkit-scrollbar-thumb {
    background: #eee;
    border-radius: 2px;
}

/* Task Card */
.task-card {
    background: white;
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    border: 1px solid rgba(0,0,0,0.04);
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: transform 0.2s, box-shadow 0.2s;
}
.task-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.card-content {
    flex: 1;
    min-width: 0; 
    padding-right: 12px;
}
.card-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
}
.task-title {
    font-weight: 600;
    font-size: 0.95em;
    color: #333;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.time-tag {
    font-size: 0.75em;
    color: #999;
    background: rgba(255,255,255,0.6);
    padding: 2px 6px;
    border-radius: 4px;
}
.card-desc {
    font-size: 0.85em;
    color: #666;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.4;
}
.done-btn {
    background: #52c41a;
    border-color: #52c41a;
    box-shadow: 0 2px 6px rgba(82, 196, 26, 0.3);
}
.done-btn:hover {
    background: #73d13d;
    border-color: #73d13d;
}

/* Settings Modal */
.setting-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}
</style>
