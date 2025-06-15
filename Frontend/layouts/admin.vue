<template>
  <div :class="layoutWrapper">
    <AdminSidebar :class="sidebarClass" />

    <div :class="contentWrapper">
      <AdminNavbar v-if="!route.meta.noHeader" />

      <main :class="mainContent">
        <NuxtPage />
      </main>

      <AdminFooter v-if="!route.meta.noHeader" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import AdminSidebar from "~/views/admin/layouts/SidebarView.vue";
import AdminNavbar from "~/views//admin/layouts/NavbarView.vue";
import AdminFooter from "~/views/admin/layouts/FooterView.vue";

// Tailwind layout classes defined in JS
const layoutWrapper = "min-h-screen flex bg-gray-50 dark:bg-gray-900";
const sidebarClass = "h-screen w-64 flex-shrink-0 overflow-y-auto";
const contentWrapper = "flex-1 flex flex-col min-h-screen";
const mainContent = "flex-1 overflow-auto";

const route = useRoute();
</script>
