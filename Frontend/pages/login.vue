<template>
  <Transition name="fade-slide" appear>
    <div
      class="max-w-md mx-auto mt-16 p-8 rounded-lg shadow-lg bg-white text-center font-sans">
      <!-- School Logo -->
      <img
        :src="schoolLogo"
        alt="School Logo"
        class="w-40 sm:w-72 mx-auto mb-8 select-none" />

      <!-- Login Form -->
      <el-form
        :model="form"
        label-position="top"
        @submit.prevent="login"
        class="text-left">
        <el-form-item
          label="username"
          :rules="[
            {
              required: true,
              message: 'Please enter username',
              trigger: 'blur',
            },
          ]"
          class="mb-6">
          <el-input
            v-model="form.username"
            placeholder="username"
            autocomplete="username"
            class="rounded-md text-[var(--color-dark)] placeholder:[var(--color-primary-light)]" />
        </el-form-item>

        <el-form-item
          label="Password"
          :rules="[
            {
              required: true,
              message: 'Please enter password',
              trigger: 'blur',
            },
          ]"
          class="mb-6">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="Password"
            autocomplete="current-password"
            show-password
            class="rounded-md text-[var(--color-dark)] placeholder:[var(--color-primary-light)]" />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            class="w-full rounded-md font-semibold shadow-md"
            style="
              background-color: var(--color-primary);
              color: var(--color-light);
            "
            @mouseover="hover = true"
            @mouseleave="hover = false"
            :style="
              hover ? 'background-color: var(--color-primary-light);' : ''
            ">
            Login
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Google Login Button -->
      <el-button
        class="w-full mt-2 flex items-center justify-center gap-2 border rounded-md"
        @click="loginWithGoogle"
        @mouseover="hoverGoogle = true"
        @mouseleave="hoverGoogle = false">
        <img :src="googleIcon" alt="Google Icon" class="w-7 h-7 m-2" />
        <span>Login with Google</span>
      </el-button>

      <!-- Register Link -->
      <p
        class="text-sm text-center mt-4"
        :style="{ color: 'var(--color-dark)' }">
        Don't have an account?
        <RouterLink
          to="/register"
          class="hover:underline"
          :style="{ color: 'var(--color-primary)' }">
          Register here
        </RouterLink>
      </p>
    </div>
  </Transition>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useFetch, useCookie } from "#app";
import { ElMessage } from "element-plus";

import schoolLogo from "@/assets/logo/ppiu.png";
import googleIcon from "@/assets/svg/googleIcon.svg";

const router = useRouter();
const loading = ref(false);

const hover = ref(false);
const hoverGoogle = ref(false);

const form = reactive({
  username: "",
  password: "",
});

const login = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning("Please fill in all fields");
    return;
  }
  loading.value = true;
  try {
    const { data, error } = await useFetch("http://127.0.0.1:5000/auth/login", {
      method: "POST",
      body: { username: form.username, password: form.password },
    });
    if (error.value) {
      ElMessage.error("Login failed");
      return;
    }
    const user = data.value.user;
    useCookie("user").value = user;
    useCookie("token").value = data.value.token;
    ElMessage.success("Login successful");

    router.push("/home");
  } catch {
    ElMessage.error("Something went wrong");
  } finally {
    loading.value = false;
  }
};

const loginWithGoogle = () => {
  window.location.href = "http://localhost:5000/auth/google/login";
};

onMounted(() => {
  const token = useCookie("token").value;
  const user = useCookie("user").value;
  if (token && user?.role) {
    if (user.role === "admin") router.push("/admin");
    else if (user.role === "teacher") router.push("/teacher");
    else router.push("/student");
  }
});
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}
.fade-slide-enter-to {
  opacity: 1;
  transform: translateY(0);
}
.fade-slide-leave-from {
  opacity: 1;
  transform: translateY(0);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
