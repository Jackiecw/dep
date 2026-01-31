<template>
  <div>
    <div style="margin-bottom: 16px; display: flex; justify-content: space-between;">
        <h2>User Management</h2>
        <a-button type="primary" @click="showCreateModal">Add User</a-button>
    </div>

    <a-table :columns="columns" :data-source="users" :loading="loading" rowKey="id">
        <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'role'">
                <a-tag :color="record.role === 'admin' ? 'red' : 'blue'">
                    {{ record.role.toUpperCase() }}
                </a-tag>
            </template>
            <template v-else-if="column.key === 'is_active'">
                <a-badge :status="record.is_active ? 'success' : 'default'" :text="record.is_active ? 'Active' : 'Disabled'" />
            </template>
            <template v-else-if="column.key === 'action'">
                <a-space>
                    <a-button size="small" @click="editUser(record)">Edit</a-button>
                    <!-- Simple toggle active for now, or reset password -->
                    <!-- <a-button size="small" danger>Disable</a-button> -->
                </a-space>
            </template>
        </template>
    </a-table>

    <a-modal
        v-model:open="modalVisible"
        :title="isEdit ? 'Edit User' : 'Create User'"
        @ok="handleOk"
        :confirmLoading="modalLoading"
    >
        <a-form layout="vertical">
            <a-form-item label="Username" required>
                <a-input v-model:value="formState.username" :disabled="isEdit" />
            </a-form-item>
            <a-form-item label="Display Name" required>
                <a-input v-model:value="formState.display_name" />
            </a-form-item>
            <a-form-item label="Role" required>
                <a-select v-model:value="formState.role">
                    <a-select-option value="employee">Employee</a-select-option>
                    <a-select-option value="admin">Admin</a-select-option>
                </a-select>
            </a-form-item>
            <a-form-item label="Password" :required="!isEdit">
                <a-input-password v-model:value="formState.password" :placeholder="isEdit ? 'Leave empty to keep unchanged' : ''" />
            </a-form-item>
        </a-form>
    </a-modal>
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
    role: string;
    is_active: boolean;
}

const users = ref<User[]>([]);
const loading = ref(false);
const modalVisible = ref(false);
const modalLoading = ref(false);
const isEdit = ref(false);

const formState = reactive({
    id: 0, // for edit
    username: '',
    display_name: '',
    role: 'employee',
    password: ''
});

const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: 'Username', dataIndex: 'username', key: 'username' },
    { title: 'Display Name', dataIndex: 'display_name', key: 'display_name' },
    { title: 'Role', dataIndex: 'role', key: 'role' },
    { title: 'Status', key: 'is_active', width: 100 },
    { title: 'Action', key: 'action', width: 150 },
];

onMounted(() => {
    fetchUsers();
});

async function fetchUsers() {
    loading.value = true;
    try {
        const res = await api.get('/users');
        users.value = res.data;
    } catch (e) {
        message.error('Failed to fetch users');
    } finally {
        loading.value = false;
    }
}

function showCreateModal() {
    isEdit.value = false;
    formState.username = '';
    formState.display_name = '';
    formState.role = 'employee';
    formState.password = '';
    modalVisible.value = true;
}

function editUser(_user: User) {
    // In a real app we might fetch user details or just use what we have
    // Note: The API currently doesn't support full user editing (only create).
    // The plan said "User Management UI (CRUD)".
    // Backend Implementation Phase 1 only had `POST /users` (Create).
    // EDIT & DELETE API endpoints are missing in `api.py`.
    // I should probably stick to Create for now as per "Phase 1 backend".
    // Or I should implement Edit in Backend?
    // Let's implement CREATE only for now to match current backend, 
    // and maybe mock Edit or add Backend support if needed.
    
    // Actually, task.md "Phase 2" implies I should do what's needed.
    // But I am in Client Development.
    // Let's stick to Create User for now as MVP.
    message.info("Edit function not yet implemented in backend");
}

async function handleOk() {
    if (!formState.username || !formState.display_name) {
        message.warn("Please fill required fields");
        return;
    }
    
    modalLoading.value = true;
    try {
        if (!isEdit.value) {
            await api.post('/users', {
                username: formState.username,
                password: formState.password,
                display_name: formState.display_name,
                role: formState.role
            });
            message.success('User created');
            modalVisible.value = false;
            fetchUsers();
        }
    } catch (e: any) {
        message.error("Error: " + (e.response?.data?.detail || e.message));
    } finally {
        modalLoading.value = false;
    }
}
</script>
