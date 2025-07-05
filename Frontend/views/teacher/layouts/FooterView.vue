<script lang="ts" setup>
import AppFooter from "~/components/layout/AppFooter.vue";
const footerClass = "bg-white shadow px-4 py-2";
const leftSectionClass = "flex items-center";
const rightSectionClass = "flex items-center";
</script>

<template>
  <AppFooter
    :footer-class="footerClass"
    :left-section-class="leftSectionClass"
    :right-section-class="rightSectionClass"
  />
</template>
