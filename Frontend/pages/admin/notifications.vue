<script setup lang="ts">
definePageMeta({
  layout: "admin",
});
import FullCalendarKH from "~/components/Calendar/CambodiaCalendar.vue";
</script>

<template>
  <div>
    <h2 class="text-2xl font-semibold mb-4">Dashboard</h2>
    <el-card class="p-6">
      <p>Welcome to the Admin Dashboard!</p>
      <!-- Add your widgets and stats here -->
    </el-card>
  </div>

  <div class="p-4">
    <h1 class="text-xl font-bold mb-4">🇰🇭 Cambodian Holidays</h1>
    <FullCalendarKH />
  </div>
</template>
