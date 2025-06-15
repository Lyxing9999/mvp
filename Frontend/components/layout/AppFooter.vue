<template>
  <el-footer :class="props.footerClass">
    © 2025 Your Company. All rights reserved.
  </el-footer>
</template>

<script setup lang="ts">
import { defineProps } from "vue";
import { footerClass } from "~/constants/tailwind/layoutDefaultClasses";

const props = defineProps({
  footerClass: { type: String, default: footerClass },
});
</script>
