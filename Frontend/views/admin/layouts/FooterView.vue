<script lang="ts" setup>
import AppFooter from "~/components/layout/AppFooter.vue";
const footerClass =
  "h-10 bg-white dark:bg-red-600 text-center text-gray-500 dark:text-red-200 text-sm flex items-center justify-center";

</script>

<template>
  <AppFooter :footer-class="footerClass" />
</template>
