<script lang="ts" setup>
import { menus } from "~/constants/menus";
import BaseSideBar from "~/components/Base/BaseSideBar.vue";
const 
</script>

<template>
  <AppSidebar
    :is-mobile="false"
    :is-collapsed="false"
    :aside-class="asideClass"
    :logo-container-class="logoContainerClass"
    :logo-wrapper-class="logoWrapperClass"
    :logo-img-class="logoImgClass"
    :menu-items="menuItems"
  />
</template>
