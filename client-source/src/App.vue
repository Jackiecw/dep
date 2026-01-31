<template>
  <a-config-provider>
    <Login v-if="!authStore.isAuthenticated" />
    <router-view v-else />
    
    <a-modal
      v-model:open="updateVisible"
      title="New Version Available"
      ok-text="Update Now"
      @ok="handleUpdate"
      :closable="false"
      :maskClosable="false"
    >
      <p>A new version ({{ remoteVersion }}) is available.</p>
      <p>Notes: {{ updateNotes }}</p>
    </a-modal>
  </a-config-provider>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useAuthStore } from './stores/auth';
import { useSettingsStore } from './stores/settings';
import { getVersion } from '@tauri-apps/api/app';
import { open } from '@tauri-apps/plugin-shell';
import { setWindowMode } from './utils/windowManager'; // Import helper
import Login from './views/Login.vue';
import axios from 'axios';
import { listen } from '@tauri-apps/api/event';
import { getCurrentWindow } from '@tauri-apps/api/window';
import { exit } from '@tauri-apps/plugin-process';

const authStore = useAuthStore();
const settingsStore = useSettingsStore();

// Handle Close Request
listen('close-requested', async () => {
    if (!settingsStore.closeBehavior || settingsStore.closeBehavior === 'minimize') {
        await getCurrentWindow().hide();
    } else {
        await exit(0);
    }
});



const updateVisible = ref(false);
const remoteVersion = ref('');
const updateUrl = ref('');
const updateNotes = ref('');

// Watch user state to enforce window size
watch(() => authStore.user, async (user) => {
    if (user) {
        if (user.role === 'admin') await setWindowMode('admin');
        else await setWindowMode('widget');
    }
}, { immediate: true });

onMounted(async () => {
    await settingsStore.init();
    await checkVersion();
});

async function checkVersion() {
    try {
        // Fetch remote version
        const res = await axios.get('http://localhost:8000/static/version.json');
        const remote = res.data;
        
        // Get local version
        // Note: getVersion returns a Promise<string>
        const local = await getVersion();
        
        if (compareVersions(remote.version, local) > 0) {
            remoteVersion.value = remote.version;
            updateUrl.value = remote.url;
            updateNotes.value = remote.notes;
            updateVisible.value = true;
        }
    } catch (e) {
        console.error("Failed to check version", e);
    }
}

function handleUpdate() {
    if (updateUrl.value) {
        // Open URL in default browser
        open(updateUrl.value);
    }
}

function compareVersions(v1: string, v2: string) {
    const p1 = v1.split('.').map(Number);
    const p2 = v2.split('.').map(Number);
    for (let i = 0; i < Math.max(p1.length, p2.length); i++) {
        const n1 = p1[i] || 0;
        const n2 = p2[i] || 0;
        if (n1 > n2) return 1;
        if (n1 < n2) return -1;
    }
    return 0;
}
</script>

<style>
body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: transparent; 
}
</style>