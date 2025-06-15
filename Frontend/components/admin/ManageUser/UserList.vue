<script lang="ts" setup>
import { ref, onMounted, computed } from "vue";
import { UserService } from "~/services/userService";
import { UserModel } from "~/models/userModel";
import type { User } from "~/types/User";
import type { UserDetail } from "~/types/userServiceInterface";
import { Timer } from "@element-plus/icons-vue";
import { formatDate } from "~/utils/formatDate";
import UserDetailDialog from "~/components/Base/UserDetailDialog.vue";

const loading = ref(false);
const showDialog = ref(false);
const showEditDialog = ref(false);
const userDetails = ref<UserDetail>(null);
const dialogLoading = ref(false);
const users = ref<UserModel[]>([]);
const editForm = ref<Partial<User>>({});
const currentPage = ref(1);
const pageSize = ref(20);
const userService = new UserService();

async function fetchUsers() {
  loading.value = true;
  try {
    const usersArray = await userService.listUsers();
    users.value = usersArray.map((user) => new UserModel(user));
  } catch (error) {
    console.error("Failed to fetch users:", error);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchUsers();
});

async function handleDetail(id: string) {
  try {
    dialogLoading.value = true;
    const response = await userService.getUserDetails(id);
    userDetails.value = response;
    showDialog.value = true;
  } catch (err) {
    console.error("❌ Failed to fetch user details:", err);
  } finally {
    dialogLoading.value = false;
  }
}

function handleEdit(user: User) {
  editForm.value = { ...user }; // clone to prevent direct mutation
  showEditDialog.value = true;
}

async function submitEdit() {
  try {
    await userService.updateUser(editForm.value._id as string, editForm.value);
    console.log("✅ User updated:", editForm.value);
    showEditDialog.value = false;
    fetchUsers(); // refresh table
  } catch (err) {
    console.error("❌ Failed to update user:", err);
  }
}

function handleDelete(user: User) {
  console.log("Delete user", user);
  // Add delete logic if needed
}

const pagedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return users.value.slice(start, start + pageSize.value);
});

function handlePageChange(page: number) {
  currentPage.value = page;
}

// For inline editing
const editing = ref<{ id: string | null; field: "username" | "email" | null }>({
  id: null,
  field: null,
});

// Store original value before editing
const originalValue = ref<{ username?: string; email?: string }>({});

function startEditing(row: UserModel, field: "username" | "email") {
  editing.value = { id: row._id, field };
  if (field === "username") {
    originalValue.value.username = row.username;
  } else if (field === "email") {
    originalValue.value.email = row.email;
  }
}

// On blur, check if changed; if no change undo edit, else submit
async function onBlurEdit(row: UserModel, field: "username" | "email") {
  if (
    (field === "username" && row.username === originalValue.value.username) ||
    (field === "email" && row.email === originalValue.value.email)
  ) {
    // No change, cancel editing and restore original value (to be safe)
    if (field === "username") {
      row.username = originalValue.value.username!;
    } else {
      row.email = originalValue.value.email!;
    }
    editing.value = { id: null, field: null };
  } else {
    // Value changed, submit update
    await submitInlineEdit(row);
  }
}

async function submitInlineEdit(row: UserModel) {
  try {
    await userService.updateUser(row._id, {
      username: row.username,
      email: row.email,
      role: row.role,
    });
    editing.value = { id: null, field: null };
    fetchUsers(); // Refresh after save
  } catch (error) {
    console.error("Failed to save inline edit:", error);
  }
}
</script>

<template>
  <el-skeleton
    v-show="loading"
    :rows="10"
    animated
    border
    class="h-full"
    :loading="loading" />

  <el-table
    :data="pagedUsers"
    border
    stripe
    class="w-full"
    :header-cell-style="
      ({ column }) => {
        if (column.property === 'role') {
          return {
            textAlign: 'center',
            backgroundColor: '#f8f9fa',
            color: 'var(--color-secondary)',
            fontWeight: '600',
            fontSize: '14px',
          };
        }
        return {
          backgroundColor: '#f8f9fa',
          color: 'var(--color-secondary)',
          fontWeight: '600',
          fontSize: '14px',
          textAlign: 'left',
        };
      }
    ">
    <el-table-column label="Username" width="180" align="left">
      <template #default="{ row }">
        <div class="flex items-center space-x-2">
          <template
            v-if="editing.id === row._id && editing.field === 'username'">
            <el-input
              v-model="row.username"
              size="small"
              class="w-32"
              @keyup.enter="submitInlineEdit(row)"
              @blur="() => onBlurEdit(row, 'username')" />
          </template>
          <template v-else>
            <span>{{ row.username }}</span>
            <el-button
              icon="Edit"
              link
              size="small"
              @click="() => startEditing(row, 'username')" />
          </template>
        </div>
      </template>
    </el-table-column>

    <el-table-column label="Email" width="250" align="left">
      <template #default="{ row }">
        <div class="flex items-center space-x-2">
          <template v-if="editing.id === row._id && editing.field === 'email'">
            <el-input
              v-model="row.email"
              size="small"
              class="w-48"
              @keyup.enter="submitInlineEdit(row)"
              @blur="() => onBlurEdit(row, 'email')" />
          </template>
          <template v-else>
            <span>{{ row.email ?? "No email provided" }}</span>
            <el-button
              icon="Edit"
              link
              size="small"
              @click="() => startEditing(row, 'email')" />
          </template>
        </div>
      </template>
    </el-table-column>

    <el-table-column prop="role" align="center" label="Role" width="160">
      <template #default="{ row }">
        <el-tag
          v-if="(row as UserModel).role === 'admin'"
          type="info"
          size="small"
          >Admin</el-tag
        >
        <el-tag
          v-else-if="(row as UserModel).role === 'teacher'"
          type="primary"
          size="small"
          >Teacher</el-tag
        >
        <el-tag
          v-else-if="(row as UserModel).role === 'student'"
          type="success"
          size="small"
          >Student</el-tag
        >
        <span v-else>Unknown Role</span>
      </template>
    </el-table-column>

    <el-table-column prop="_id" label="ID" width="250" />
    <el-table-column label="Created At" align="center" width="200">
      <template #default="{ row }">
        {{ formatDate((row as UserModel).createdAt) }}
        <el-icon><Timer /></el-icon>
      </template>
    </el-table-column>

    <el-table-column fixed="right" label="Operations" min-width="220">
      <template #default="{ row }">
        <el-button
          link
          type="primary"
          size="small"
          @click="handleDetail(row._id)"
          >Detail</el-button
        >
        <el-button link type="primary" size="small" @click="handleEdit(row)"
          >Edit</el-button
        >
        <el-button link type="danger" size="small" @click="handleDelete(row)"
          >Delete</el-button
        >
      </template>
    </el-table-column>
  </el-table>

  <div v-if="!loading && users.length === 0" class="text-center mt-4">
    No users found.
  </div>

  <div class="flex justify-end mt-4">
    <el-pagination
      background
      layout="prev, pager, next"
      :total="users.length"
      :page-size="pageSize"
      :current-page="currentPage"
      @current-change="handlePageChange" />
  </div>

  <UserDetailDialog
    :user-details="userDetails"
    v-model="showDialog"
    :loading="dialogLoading" />
</template>
