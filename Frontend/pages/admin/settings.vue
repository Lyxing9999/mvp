<script setup lang="ts">
definePageMeta({
  layout: "admin",
});

import UserList from "~/components/Admin/ManageUser/UserList.vue";
</script>

<template>
  <div>
    <UserList />
  </div>
</template>
