<template>
  <a-config-provider>
    <div class="container">
      <h1>Internal Task System</h1>
      <a-space>
        <a-button type="primary" @click="greet">Ping Server</a-button>
        <a-button @click="checkVersion">Check Version</a-button>
      </a-space>
      <div style="margin-top: 20px">
        <p>{{ greetMsg }}</p>
      </div>
    </div>
  </a-config-provider>
</template>

<script setup lang="ts">
import { ref } from "vue";
import axios from "axios";

const greetMsg = ref("");

async function greet() {
  try {
    // Basic connectivity check to our local API
    const res = await axios.get("http://localhost:8000/");
    greetMsg.value = res.data.message;
  } catch (error) {
    greetMsg.value = "Error connecting to server: " + error;
  }
}

async function checkVersion() {
    try {
        const res = await axios.get("http://localhost:8000/static/version.json");
        greetMsg.value = "Version: " + JSON.stringify(res.data);
    } catch (error) {
        greetMsg.value = "Error checking version: " + error;
    }
}
</script>

<style scoped>
.container {
  padding: 20px;
  text-align: center;
}
</style>