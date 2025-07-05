<script lang="ts" setup>
import HeaderView from "~/views/teacher/layouts/HeaderView.vue";
import FooterView from "~/views/teacher/layouts/FooterView.vue";
import SidebarView from "~/views/teacher/layouts/SidebarView.vue";
import CambodiaCalendar from "~/components/Calendar/CambodiaCalendar.vue";
const activeTab = ref("charts");
</script>

<template>
  <el-container>
    <el-header>
      <HeaderView />
    </el-header>
    <el-container>
      <el-aside>
        <SidebarView />
      </el-aside>
      <el-main>
        <el-row :gutter="20">
          <el-col :xs="24" :xl="16">
            <h1>Dashboard</h1>
          </el-col>
          <el-col :xl="8">
            <CambodiaCalendar />
          </el-col>
        </el-row>
        <el-col :xs="24" :xl="16">
          <slot />
        </el-col>
        <el-col :xl="8">
          <CambodiaCalendar />
        </el-col>
      </el-main>
    </el-container>
    <el-footer>
      <FooterView />
    </el-footer>
  </el-container>
</template>
