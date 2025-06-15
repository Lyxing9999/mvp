<template>
  <el-aside :class="props.asideClass">
    <!-- Toggle Collapse -->
    <el-radio-group v-model="isCollapsed" class="p-2 flex justify-center">
      <el-radio-button :value="false">Expand</el-radio-button>
      <el-radio-button :value="true">Collapse</el-radio-button>
    </el-radio-group>

    <!-- Logo -->
    <div :class="props.logoContainerClass">
      <div :class="props.logoWrapperClass">
        <img :src="schoolLogo" alt="School Logo" :class="props.logoImgClass" />
      </div>
    </div>

    <!-- Menu -->
    <el-menu
      :default-active="activeMenu"
      background-color="transparent"
      text-color="var(--menu-text-color)"
      active-text-color="var(--color-primary)"
      router
      :collapse="isCollapsed"
      :class="props.menuClass">
      <el-menu-item
        v-for="item in menuItems"
        :key="item.route"
        :index="item.route"
        :title="item.title">
        <el-icon>
          <component :is="item.icon" />
        </el-icon>
        <template #title>
          <span :class="props.menuTitleClass">{{ item.title }}</span>
        </template>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>
<script setup lang="ts">
import { ref, computed } from "vue";
import { useRoute } from "vue-router";
import schoolLogo from "~/assets/image/ppiu_logo.png";
import { menus } from "~/constants/menus";
import { useAuthStore } from "~/stores/authStore";

import {
  asideClass,
  logoContainerClass,
  logoWrapperClass,
  logoImgClass,
  menuClass,
  menuTitleClass,
} from "~/constants/tailwind/layoutDefaultClasses";

import {
  HomeFilled,
  User,
  Notebook,
  Bell,
  Calendar,
  Setting,
} from "@element-plus/icons-vue";

const isCollapsed = ref(false); // 👈 collapse toggle

const props = withDefaults(
  defineProps<{
    asideClass?: string;
    logoContainerClass?: string;
    logoWrapperClass?: string;
    logoImgClass?: string;
    menuClass?: string;
    menuTitleClass?: string;
  }>(),
  {
    asideClass,
    logoContainerClass,
    logoWrapperClass,
    logoImgClass,
    menuClass,
    menuTitleClass,
  }
);

type MenuItem = {
  title: string;
  icon: keyof typeof iconMap;
  route: string;
};

const iconMap = {
  HomeFilled,
  User,
  Notebook,
  Bell,
  Calendar,
  Setting,
};

const authStore = useAuthStore();
const role = computed(() => authStore.user?.role);

const menuItems = computed(() =>
  (menus[role.value as keyof typeof menus] || []).map((item: MenuItem) => ({
    ...item,
    icon: iconMap[item.icon] || HomeFilled,
  }))
);

const route = useRoute();
const activeMenu = computed(() => route.path);
</script>
