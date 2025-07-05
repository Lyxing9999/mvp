<script lang="ts" setup>
import TeacherSidebar from "~/views/teacher/layouts/SidebarView.vue";
import TeacherHeader from "~/views/teacher/layouts/HeaderView.vue";
import TeacherFooter from "~/views/teacher/layouts/FooterView.vue";

const containerClass = "min-h-screen bg-gray-50 dark:bg-gray-900";
const asideClass = "h-screen overflow-y-auto";
const headerHeight = "64px";
const footerHeight = "50px";
const mainClass = "overflow-auto";
const footerClass = "bg-white shadow px-4 py-2";
const leftSectionClass = "flex items-center";
const rightSectionClass = "flex items-center";
</script>
<template>
  <el-container :class="containerClass">
    <el-header>
      <TeacherHeader />
    </el-header>
    <el-container>
      <el-aside :class="asideClass">
        <TeacherSidebar />
      </el-aside>
      <el-main :class="mainClass">
        <slot />
      </el-main>
    </el-container>
    <el-footer :class="footerClass">
      <TeacherFooter />
    </el-footer>
  </el-container>
</template>
