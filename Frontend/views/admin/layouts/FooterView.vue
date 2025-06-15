<script lang="ts" setup>
import AppFooter from "~/components/layout/AppFooter.vue";
import { footerClass } from "~/constants/tailwind/layoutAdminClasses";
</script>

<template>
  <AppFooter :footer-class="footerClass" />
</template>
