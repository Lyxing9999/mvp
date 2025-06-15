<script setup lang="ts">
definePageMeta({
  layout: "admin",
});
import Dashboard from "~/views/admin/Dashboard/index.vue";
</script>

<template>
  <el-card class="w-full h-full">
    <Dashboard />
  </el-card>
</template>
