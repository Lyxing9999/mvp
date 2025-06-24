// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";
import { visualizer } from "rollup-plugin-visualizer";

export default defineNuxtConfig({
  compatibilityDate: "2025-05-29",
  modules: ["@element-plus/nuxt", "@pinia/nuxt"],
  devtools: true,
  css: ["@/styles/css/main.css", "@/styles/scss/calendar-styles.scss"],
  vite: {
    plugins: [tailwindcss(), visualizer({ open: false })],
    define: {
      __DEV__: true,
    },
    server: {
      watch: {
        usePolling: true,
      },
      host: true,
    },
  },
  ssr: false,
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE,
    },
  },
  router: {
    middleware: ["auth"],
  },
  darkMode: "class",
  optimizeDeps: {
    include: [
      "@fullcalendar/core",
      "@fullcalendar/daygrid",
      "@fullcalendar/interaction",
    ],
  },
  app: {
    head: {
      script: [
        {
          children: `(function() {
            try {
              if (localStorage.getItem('dark') === 'true') {
                document.documentElement.classList.add('dark');
              }
            } catch(_) {}
          })();`,
        },
      ],
    },
  },
});
