<template>
  <el-header :class="props.headerClass">
    <div :class="props.leftSectionClass">
      <button
        @click="$emit('toggle-sidebar')"
        :class="props.toggleButtonClass"
        aria-label="Toggle sidebar">
        <el-icon><Menu /></el-icon>
      </button>
    </div>

    <el-input
      v-model="searchQuery"
      placeholder="Search..."
      clearable
      size="small"
      :class="props.searchInputClass"
      @clear="onClear"
      @keyup.enter.native="onSearch">
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
    </el-input>

    <div :class="props.rightSectionClass">
      <el-tooltip content="Notifications" placement="bottom">
        <el-badge
          :value="notificationCount"
          :class="props.notificationBadgeClass"
          @click="onNotificationClick">
          <el-icon><Bell /></el-icon>
        </el-badge>
      </el-tooltip>

      <button
        @click="toggleDark"
        :class="props.darkModeButtonClass"
        aria-label="Toggle dark mode">
        <el-icon v-if="isDark"><Sunny /></el-icon>
        <el-icon v-else><Moon /></el-icon>
      </button>

      <el-dropdown trigger="click" placement="bottom-end">
        <span :class="props.userDropdownTriggerClass">
          <el-avatar size="32" icon="el-icon-user" />
          <span :class="props.userNameClass">{{ userName }}</span>
          <el-icon><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="onProfileClick">Profile</el-dropdown-item>
            <el-dropdown-item divided @click="onLogoutClick"
              >Logout</el-dropdown-item
            >
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { ref } from "vue";
import {
  Menu,
  Search,
  Bell,
  Sunny,
  Moon,
  ArrowDown,
} from "@element-plus/icons-vue";

import {
  headerClass,
  leftSectionClass,
  toggleButtonClass,
  searchInputClass,
  rightSectionClass,
  notificationBadgeClass,
  darkModeButtonClass,
  userDropdownTriggerClass,
  userNameClass,
} from "~/constants/tailwind/layoutDefaultClasses";
const props = withDefaults(
  defineProps<{
    headerClass?: string;
    leftSectionClass?: string;
    toggleButtonClass?: string;
    searchInputClass?: string;
    rightSectionClass?: string;
    notificationBadgeClass?: string;
    darkModeButtonClass?: string;
    userDropdownTriggerClass?: string;
    userNameClass?: string;
  }>(),
  {
    headerClass,
    leftSectionClass,
    toggleButtonClass,
    searchInputClass,
    rightSectionClass,
    notificationBadgeClass,
    darkModeButtonClass,
    userDropdownTriggerClass,
    userNameClass,
  }
);

// Emits
defineEmits(["toggle-sidebar"]);

// State
const searchQuery = ref("");
const notificationCount = ref(3);
const userName = ref("Admin User");

// Events
function onSearch() {
  alert(`Search for: ${searchQuery.value}`);
}
function onClear() {
  console.log("Search cleared");
}
function onNotificationClick() {
  alert("Notifications clicked");
}
function onProfileClick() {
  alert("Go to profile");
}
function onLogoutClick() {
  alert("Logging out...");
}

// Dark mode toggle
import { useDarkMode } from "@/composables/useDarkMode";
const { isDark, toggleDark } = useDarkMode();
</script>
