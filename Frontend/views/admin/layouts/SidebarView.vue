<script lang="ts" setup>
import AppSidebar from "~/components/layout/AppSidebar.vue";
import {
  asideClass,
  logoContainerClass,
  logoWrapperClass,
  logoImgClass,
  menuClass,
  menuTitleClass,
} from "~/constants/tailwind/layoutAdminClasses";
</script>

<template>
  <AppSidebar
    :aside-class="asideClass"
    :logo-container-class="logoContainerClass"
    :logo-wrapper-class="logoWrapperClass"
    :logo-img-class="logoImgClass"
    :menu-class="menuClass"
    :menu-title-class="menuTitleClass" />
</template>
