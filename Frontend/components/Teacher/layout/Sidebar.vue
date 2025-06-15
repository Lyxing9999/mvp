<template>
  <el-aside
    width="220px"
    class="bg-white dark:bg-gray-800 shadow-lg h-full flex flex-col">
    <div class="p-4 flex justify-center items-center mb-4">
      <img
        :src="schoolLogo"
        alt="School Logo"
        class="h-20 w-auto select-none" />
    </div>

    <el-menu
      :default-active="activeMenu"
      class="flex-1"
      background-color="transparent"
      text-color="#909399"
      active-text-color="#409EFF"
      router>
      <el-menu-item index="/teacher/dashboard">
        <el-icon><HomeFilled /></el-icon>
        Dashboard
      </el-menu-item>

      <el-menu-item index="/teacher/attendance"> Attendance </el-menu-item>

      <el-menu-item index="/teacher/students">
        <el-icon><User /></el-icon>
        Students
      </el-menu-item>

      <el-menu-item index="/teacher/grades-comments">
        <el-icon><Edit /></el-icon>
        Grades & Comments
      </el-menu-item>

      <el-menu-item index="/teacher/classes">
        <el-icon><Folder /></el-icon>
        Classes
      </el-menu-item>

      <el-menu-item index="/teacher/notifications">
        <el-icon><Bell /></el-icon>
        Notifications
      </el-menu-item>

      <el-menu-item index="/teacher/profile">
        <el-icon><UserFilled /></el-icon>
        Profile
      </el-menu-item>
    </el-menu>

    <div class="p-4 text-sm text-gray-400 text-center">
      © 2025 Your Company
    </div>
  </el-aside>
</template>

<script setup>
import { useRoute } from "vue-router";
import schoolLogo from "~/assets/image/ppiu_logo.png";

const route = useRoute();
const activeMenu = route.path;
</script>
