<script setup lang="ts">
definePageMeta({
  layout: "admin",
});

import AdvancedUserTable from "~/components/admin/AdvancedUserTable.vue";
</script>

<template>
  <el-card>
    <AdvancedUserTable />
  </el-card>
</template>
