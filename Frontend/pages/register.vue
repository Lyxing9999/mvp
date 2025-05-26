<template>
  <Transition name="fade-slide" appear>
    <div
      class="max-w-md mx-auto mt-16 p-8 rounded-lg shadow-lg bg-white text-center font-inter">
      <h2
        class="text-2xl font-semibold mb-6"
        :style="{ color: 'var(--color-dark)' }">
        Register
      </h2>

      <el-form
        :model="form"
        class="text-left"
        @submit.prevent="register"
        label-position="top">
        <el-form-item
          class="mb-6"
          label="username"
          :rules="[
            { required: true, message: 'Please input email', trigger: 'blur' },
          ]">
          <el-input
            v-model="form.username"
            placeholder="Enter your username"
            autocomplete="username"
            class="text-[var(--color-dark)] placeholder:[var(--color-primary-light)] rounded-md" />
        </el-form-item>

        <el-form-item
          label="Password"
          :rules="[
            {
              required: true,
              message: 'Please input password',
              trigger: 'blur',
            },
          ]"
          class="mb-6">
          <el-input
            v-model="form.password"
            placeholder="Enter your password"
            type="password"
            show-password
            autocomplete="new-password"
            class="text-[var(--color-dark)] placeholder:[var(--color-primary-light)] rounded-md" />
        </el-form-item>

        <el-form-item
          label="Confirm Password"
          :rules="[
            {
              required: true,
              message: 'Please confirm your password',
              trigger: 'blur',
            },
            { validator: validateConfirmPassword, trigger: 'blur' },
          ]"
          class="mb-6">
          <el-input
            v-model="form.confirmPassword"
            placeholder="Confirm your password"
            type="password"
            show-password
            autocomplete="new-password"
            class="text-[var(--color-dark)] placeholder:[var(--color-primary-light)] rounded-md" />
        </el-form-item>

        <el-form-item>
          <label
            class="block mb-2 text-sm"
            :style="{ color: 'var(--color-dark)' }">
            Select Role
          </label>

          <el-select
            v-model="form.role"
            placeholder="Select your role"
            class="w-full rounded-md">
            <template #prefix>
              <img
                v-if="form.role"
                :src="roles.find((r) => r.value === form.role)?.icon"
                alt=""
                class="inline-block w-5 h-5 mr-2" />
            </template>
            <el-option
              v-for="role in roles"
              :key="role.value"
              :label="role.label"
              :value="role.value">
              <template #default>
                <img
                  :src="role.icon"
                  alt=""
                  class="inline-block w-5 h-5 mr-2" />
                {{ role.label }}
              </template>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item class="mb-6">
          <el-checkbox
            class="ml-2"
            v-model="form.agree"
            :style="{ color: 'var(--color-dark)' }">
            I agree to the
            <RouterLink
              to="/terms"
              class="hover:underline"
              :style="{ color: 'var(--color-primary)' }">
              Terms and Conditions
            </RouterLink>
          </el-checkbox>
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
              hover ? 'background-color: var(--color-primary-light); ' : ''
            ">
            Register
          </el-button>
        </el-form-item>
        <el-form-tem>
          <el-button
            class="w-full mt-1 flex items-center justify-center gap-2 rounded-md shadow-md border border-gray-300"
            @click="redirectToGoogle">
            <img
              src="https://developers.google.com/identity/images/g-logo.png"
              alt="Google"
              class="w-5 h-5" />
            <span class="font-medium text-sm text-gray-700"
              >Register with Google</span
            >
          </el-button>
        </el-form-tem>
      </el-form>

      <p
        class="mt-4 text-center text-sm"
        :style="{ color: 'var(--color-dark)' }">
        Already have an account?
        <RouterLink
          to="/login"
          class="hover:underline"
          :style="{ color: 'var(--color-primary)' }">
          Login here
        </RouterLink>
      </p>
    </div>
  </Transition>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import teacher from "@/assets/svg/teacherIcon.svg";
import student from "@/assets/svg/studentIcon.svg";
import admin from "@/assets/svg/adminIcon.svg";
console.log(student, teacher, admin);
const router = useRouter();
const loading = ref(false);
const hover = ref(false);

const form = reactive({
  username: "",
  password: "",
  confirmPassword: "",
  role: null,
  agree: false,
});
const roles = [
  { label: "Student", value: "student", icon: student },
  { label: "Admin", value: "admin", icon: admin },
  { label: "Teacher", value: "teacher", icon: teacher },
];

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error("Passwords do not match"));
  } else {
    callback();
  }
};

const register = async () => {
  if (
    !form.username ||
    !form.password ||
    !form.confirmPassword ||
    !form.role ||
    !form.agree
  ) {
    alert("Please fill in all fields");
    return;
  }
  if (form.password !== form.confirmPassword) {
    alert("Passwords do not match");
    return;
  }

  loading.value = true;
  try {
    console.log("Registering user:", form);
    const { error } = await useFetch("http://127.0.0.1:5000/auth/register", {
      method: "POST",
      body: {
        username: form.username,
        password: form.password,
        role: form.role,
      },
    });

    if (error.value) {
      ElMessage.error(error.value.message);
      return;
    }

    if (error.value) {
      alert("Registration failed");
      loading.value = false;
      return;
    }

    ElMessage.success("Registration successful! Please login.");
    router.push("/login");
  } catch {
    ElMessage.error("Something went wrong");
  } finally {
    loading.value = false;
  }
};
const redirectToGoogle = () => {
  window.location.href = "http://127.0.0.1:5000/auth/google";
};
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
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
  transform: translateY(20px);
}
</style>
