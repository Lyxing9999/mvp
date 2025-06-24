<script lang="ts" setup>
import AppSidebar from "~/components/layout/AppSidebar.vue";
import schoolLogo from "~/assets/image/ppiu_logo.png";
const asideClass = "el-aside bg-white shadow h-full";
const logoContainerClass = "p-4 flex justify-center items-center mb-4";
const logoWrapperClass =
  "hover:scale-105 cursor-pointer transition-transform duration-300";
const logoImgClass = "h-20 object-contain";
const menuClass = "border-none";
const menuTitleClass = "ml-2";
</script>

<template>
  <AppSidebar
    :aside-class="asideClass"
    :logo-container-class="logoContainerClass"
    :logo-wrapper-class="logoWrapperClass"
    :logo-img-class="logoImgClass"
    :menu-class="menuClass"
    :menu-title-class="menuTitleClass"
  >
    <div :class="logoContainerClass">
      <div :class="logoWrapperClass">
        <img :src="schoolLogo" :class="logoImgClass" alt="Logo" />
      </div></div
  ></AppSidebar>
</template>
