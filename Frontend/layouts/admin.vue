<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import AdminSidebar from "~/views/admin/layouts/SidebarView.vue";
import AdminHeader from "~/views/admin/layouts/HeaderView.vue";
import AdminFooter from "~/views/admin/layouts/FooterView.vue";

const route = useRoute();

const isMobile = ref(false);
const checkScreen = () => {
  isMobile.value = window.innerWidth < 800;
};
onMounted(() => {
  checkScreen();
  window.addEventListener("resize", checkScreen);
});
onUnmounted(() => {
  window.removeEventListener("resize", checkScreen);
});

const containerClass = "min-h-screen bg-gray-50 dark:bg-gray-900";
const asideClass = "h-screen overflow-y-auto";
const headerHeight = "64px";
const footerHeight = "50px";
const mainClass = "overflow-auto";

const sidebarWidth = computed(() => (isMobile.value ? "65px" : "250px"));
</script>

<template>
  <el-container :class="containerClass">
    <el-aside :width="sidebarWidth" :class="asideClass">
      <AdminSidebar :is-mobile="isMobile" />
    </el-aside>

    <el-container>
      <el-header v-if="!route.meta.noHeader" :height="headerHeight">
        <AdminHeader :is-mobile="isMobile" />
      </el-header>
      <Transition name="page" mode="out-in">
        <el-main :class="mainClass" :key="$route.fullPath">
          <NuxtPage />
        </el-main>
      </Transition>
      <el-footer v-if="!route.meta.noHeader" :height="footerHeight">
        <AdminFooter :is-mobile="isMobile" />
      </el-footer>
    </el-container>
  </el-container>
</template>
<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.25s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
