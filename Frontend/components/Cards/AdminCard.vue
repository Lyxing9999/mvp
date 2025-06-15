<template>
  <el-card class="p-4">
    <h3 class="text-lg font-semibold mb-2">Total Admins</h3>
    <div class="flex items-center gap-4">
      <img :src="adminIconColor" alt="Admin Icon" class="w-12 h-12" />

      <!-- Normal count display if growth is null or not provided -->
      <el-statistic v-if="normalCount !== undefined" :value="normalCount" />

      <!-- Colored and tagged count display -->
      <el-statistic
        v-else
        :value="count"
        :value-style="{ color: growth >= 0 ? '#3f8600' : '#cf1322' }">
        <template #suffix>
          <el-tag :type="growth >= 0 ? 'success' : 'danger'" size="medium">
            {{ growth >= 0 ? "+" : "" }}{{ growth }}%
          </el-tag>
        </template>
      </el-statistic>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { defineProps } from "vue";
import adminIconColor from "~/assets/icons/svg/admin-color.svg";

const props = defineProps<{
  count?: number;
  growth?: number;
  normalCount?: number;
}>();
</script>
