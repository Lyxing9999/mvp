<script lang="ts" setup>
import AppNavbar from "~/components/layout/AppNavbar.vue";
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
} from "~/constants/tailwind/layoutAdminClasses";
</script>

<template>
  <AppNavbar
    :header-class="headerClass"
    :left-section-class="leftSectionClass"
    :toggle-button-class="toggleButtonClass"
    :search-input-class="searchInputClass"
    :right-section-class="rightSectionClass"
    :notification-badge-class="notificationBadgeClass"
    :dark-mode-button-class="darkModeButtonClass"
    :user-dropdown-trigger-class="userDropdownTriggerClass"
    :user-name-class="userNameClass" />
</template>
