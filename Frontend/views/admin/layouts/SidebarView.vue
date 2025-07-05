<script setup lang="ts">
import BaseSideBar from "~/components/Base/BaseSideBar.vue";
import schoolLogo from "~/assets/image/ppiu_logo.png";
import { useRoute } from "vue-router";

const route = useRoute();

const sidebarClasses = {
  asideClass: "bg-[var(--color-light)] dark:bg-[var(--color-sidebar-dark)]",
  logoSectionClass:
    "p-6 mt-12 mb-6 w-2/3 mx-auto flex items-center justify-center",
  menuClass:
    "border-none   text-[var(--menu-text-color)] dark:text-[var(--color-secondary-light)]",
  menuItemClass:
    "px-4 py-3 rounded-lg  transition-colors duration-200 bg-[var(--color-sidebar-light)] dark:bg-[var(--color-sidebar-dark)] hover:bg-[var(--color-primary)] hover:text-[var(--color-light)] dark:hover:text-[var(--color-dark)]",
  menuIconClass: "text-xl leading-none text-[var(--color-primary)]",
  menuIconStyle: (item: { route: string }) => ({
    color:
      route.path === item.route
        ? "var(--color-primary)"
        : "var(--menu-text-color)",
  }),
  menuTitleClass:
    "ml-2 text-base font-semibold text-[var(--color-secondary-dark)] dark:text-[var(--color-secondary-light)]",
};
</script>

<template>
  <BaseSideBar
    :is-mobile="false"
    :logo-src="schoolLogo"
    :aside-class="sidebarClasses.asideClass"
    :logo-section-class="sidebarClasses.logoSectionClass"
    :menu-class="sidebarClasses.menuClass"
    :menu-icon-class="sidebarClasses.menuIconClass"
    :menu-icon-style="sidebarClasses.menuIconStyle"
    :menu-title-class="sidebarClasses.menuTitleClass"
  />
</template>
