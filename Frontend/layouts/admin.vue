<script setup lang="ts">
import { ref } from "vue";
import { UserModel } from "~/models/userModel";
import type { NuxtApp } from "nuxt/app";

const { $api } = useNuxtApp() as NuxtApp & { $api: any };

const userId = ref("");
const user = ref<UserModel | null>(null);
const loading = ref(false);
const errorMsg = ref("");
const successMsg = ref("");

const newUser = ref({
  username: "",
  email: "",
  role: "",
  password: "",
});

async function fetchUser(): Promise<void> {
  errorMsg.value = "";
  successMsg.value = "";
  user.value = null;

  if (!userId.value.trim()) {
    errorMsg.value = "Please enter a user ID or username";
    return;
  }

  loading.value = true;

  try {
    const res = await $api.post("/admin/search-user", {
      username: userId.value,
    });
    console.log("Fetched user:", res.data);

    if (res.data && !res.data.error) {
      console.log(res.data);
      user.value = new UserModel(res.data.data);
      console.log(user.value);
    } else {
      errorMsg.value = res.data?.error || "User not found";
    }
  } catch (err: any) {
    console.error("Fetch failed:", err.response?.data || err.message || err);
    errorMsg.value =
      err.response?.data?.error ||
      "Failed to fetch user. Please check the ID and try again.";
  } finally {
    loading.value = false;
  }
}

async function createUser() {
  errorMsg.value = "";
  successMsg.value = "";
  if (
    !newUser.value.username ||
    !newUser.value.role ||
    !newUser.value.password
  ) {
    errorMsg.value = "Please fill in all fields for new user";
    return;
  }
  loading.value = true;
  try {
    console.log(newUser.value);
    const res = await $api.post("/admin/", newUser.value);
    console.log(res.data);
    if (res.data.status) {
      successMsg.value = "User created successfully!";
      newUser.value = { username: "", email: "", role: "", password: "" };
    } else {
      errorMsg.value = res.data.msg || "Failed to create user";
    }
  } catch (err) {
    console.error("Failed to create user:", err);
    errorMsg.value = "Error creating user. Try again.";
  } finally {
    loading.value = false;
  }
}

async function updateUser() {
  if (!user.value) {
    errorMsg.value = "No user selected to update";
    return;
  }
  errorMsg.value = "";
  successMsg.value = "";
  loading.value = true;

  try {
    const res = await $api.put("/admin/", {
      _id: user.value._id,
      username: user.value.username,
      email: user.value.email,
      role: user.value.role,
    });
    // Check the response object directly
    if (res.status === 200) {
      successMsg.value = "User updated successfully!";
    } else {
      errorMsg.value = res.data || "Failed to update user";
    }
  } catch (err) {
    console.error("Failed to update user:", err);
    errorMsg.value = "Error updating user. Try again.";
  } finally {
    loading.value = false;
  }
}

async function deleteUser() {
  if (!user.value) {
    errorMsg.value = "No user selected to delete";
    return;
  }
  errorMsg.value = "";
  successMsg.value = "";
  loading.value = true;

  try {
    // Assuming your backend expects id for deletion
    const res = await $api.delete(`/admin/${user.value._id}`);
    if (res.data.status) {
      successMsg.value = "User deleted successfully!";
      user.value = null;
      userId.value = "";
    } else {
      errorMsg.value = res.data.msg || "Failed to delete user";
    }
  } catch (err) {
    console.error("Failed to delete user:", err);
    errorMsg.value = "Error deleting user. Try again.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="user-search max-w-md mx-auto p-4">
    <!-- Search -->
    <el-input
      v-model="userId"
      placeholder="Enter username or ID"
      clearable
      @keyup.enter="fetchUser" />
    <el-button
      :loading="loading"
      @click="fetchUser"
      type="primary"
      class="ml-2">
      Search
    </el-button>

    <p v-if="errorMsg" class="text-red-600 mt-2">{{ errorMsg }}</p>
    <p v-if="successMsg" class="text-green-600 mt-2">{{ successMsg }}</p>

    <!-- Show user details and edit -->
    <div v-if="user" class="mt-4 space-y-3">
      <el-input v-model="user._id" placeholder="id" />
      <el-input v-model="user.username" placeholder="Username" />
      <el-input v-model="user.email" placeholder="Email" />
      <el-input v-model="user.role" placeholder="Role" />

      <el-button :loading="loading" @click="updateUser" type="warning">
        Update User
      </el-button>
      <el-button :loading="loading" @click="deleteUser" type="danger">
        Delete User
      </el-button>
    </div>

    <hr class="my-6" />

    <!-- Create user form -->
    <div class="space-y-3">
      <h3 class="font-bold mb-2">Create New User</h3>
      <el-form :model="newUser">
        <el-form-item>
          <el-input v-model="newUser.username" placeholder="Username" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="newUser.email" placeholder="Email" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="newUser.role" placeholder="Role" />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="newUser.password"
            placeholder="Password"
            show-password
            type="password" />
        </el-form-item>
        <el-form-item>
          <el-button :loading="loading" @click="createUser" type="success">
            Create User
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.user-search {
  max-width: 400px;
  margin: auto;
  padding: 1rem;
}
</style>
