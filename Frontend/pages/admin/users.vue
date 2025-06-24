<script lang="ts" setup>
import UserListView from "~/views/admin/ManageUser/UserListView.vue";

definePageMeta({
  layout: "admin",
});
</script>

<template>
  <el-card class="w-full h-full">
    <UserListView />
  </el-card>
</template>
