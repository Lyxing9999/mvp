<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "~/stores/authStore";
import { menus } from "~/constants/menus";

import {
  HomeFilled,
  User,
  Notebook,
  Bell,
  Calendar,
  Setting,
} from "@element-plus/icons-vue";

const asideClass = "el-aside bg-white shadow h-full";
const logoContainerClass = "p-4 flex justify-center items-center mb-4";
const logoWrapperClass =
  "hover:scale-105 cursor-pointer transition-transform duration-300";
const logoImgClass = "h-20 object-contain";
const menuClass = "border-none";
const menuTitleClass = "ml-2";

const props = withDefaults(
  defineProps<{
    isMobile: boolean;
    isCollapsed?: boolean;
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

const isCollapsed = ref(false);
watch(
  () => props.isMobile,
  (val) => {
    isCollapsed.value = val;
  },
  { immediate: true }
);

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

const menuItems = computed(() => {
  const items = menus[role.value as keyof typeof menus] ?? [];
  return items.map((item) => ({
    ...item,
    icon: iconMap[item.icon as keyof typeof iconMap] ?? HomeFilled,
  }));
});

const route = useRoute();
const activeMenu = computed(() => route.path);
</script>

<template>
  <el-aside :class="props.asideClass">
    <div v-if="!props.isMobile">
      <slot />
    </div>

    <el-menu
      :default-active="activeMenu"
      background-color="transparent"
      text-color="var(--menu-text-color)"
      active-text-color="var(--color-primary)"
      router
      :collapse="isCollapsed"
      :class="props.menuClass"
    >
      <el-menu-item
        v-for="item in menuItems"
        :key="item.route"
        :index="item.route"
        :title="item.title"
      >
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
