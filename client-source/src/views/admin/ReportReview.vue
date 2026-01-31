<template>
  <div>
    <h2>Weekly Reports Review</h2>
    <a-table 
        :dataSource="reports" 
        :columns="columns" 
        rowKey="id"
        :loading="loading"
    >
        <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'content'">
                 <div class="report-content">
                    <div class="section">
                        <strong>Done:</strong>
                        <div class="text-block">{{ record.content_done }}</div>
                    </div>
                    <div class="section">
                        <strong>Plan:</strong>
                        <div class="text-block">{{ record.content_plan }}</div>
                    </div>
                    <div class="section">
                        <strong>Issues:</strong>
                        <div class="text-block">{{ record.content_issues }}</div>
                    </div>
                 </div>
            </template>
            <template v-else-if="column.key === 'user'">
                {{ record.user?.display_name }} ({{ record.user?.username }})
            </template>
            <template v-else-if="column.key === 'submitted_at'">
                <div>{{ new Date(record.submitted_at).toLocaleString() }}</div>
                <a-tag v-if="record.is_late" color="red">Late</a-tag>
            </template>
        </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import api from '../../api/request';

const loading = ref(false);
const reports = ref([]);

const columns = [
    { title: 'Week', dataIndex: 'week_num', width: 100 },
    { title: 'User', key: 'user', width: 150 },
    { title: 'Content', key: 'content' }, // Flexible width
    { title: 'Submitted', key: 'submitted_at', width: 200 },
];

onMounted(() => {
    fetchReports();
});

async function fetchReports() {
    loading.value = true;
    try {
        const res = await api.get('/reports');
        reports.value = res.data;
    } catch (e) {
        message.error("Failed to load reports");
    } finally {
        loading.value = false;
    }
}
</script>

<style scoped>
.report-content {
    font-size: 0.9em;
}
.section {
    margin-bottom: 8px;
}
.text-block {
    white-space: pre-wrap;
    background: #f5f5f5;
    padding: 4px;
    border-radius: 4px;
    margin-top: 2px;
}
</style>
