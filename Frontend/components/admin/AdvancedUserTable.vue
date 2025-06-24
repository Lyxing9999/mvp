<script lang="ts" setup>
import { ref, onMounted, computed } from "vue";
import { UserService } from "~/services/userService";
import { UserModel } from "~/models/userModel";
import type { User } from "~/types/models/User";
import type { UserDetail } from "~/types/userServiceInterface";
import { Timer } from "@element-plus/icons-vue";
import { formatDate } from "~/utils/formatDate";
import UserDetailDialog from "~/components/Base/UserDetailDialog.vue";
import MultiTypeEditCell from "~/components/Base/MultiTypeEditCell.vue";
import { unflatten } from "~/utils/unflatten";
import { convertDatesToISOString } from "~/utils/convertDatesToISOString";
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
    console.log(userDetails.value);
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
    showEditDialog.value = false;
    fetchUsers(); // refresh table
  } catch (err) {
    console.error(" Failed to update user:", err);
  }
}
function cancelEdit(row: UserModel, field: "username" | "email") {
  if (field === "username") {
    row.username = originalValue.value.username ?? row.username;
  } else if (field === "email") {
    row.email = originalValue.value.email ?? row.email;
  }
  editing.value = { id: null, field: null };
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

async function submitInlineEdit(row: UserModel) {
  try {
    console.log(row._id);
    await userService.updateUser(row._id, {
      username: row.username,
      email: row.email,
    });
    editing.value = { id: null, field: null };
    fetchUsers(); // Refresh after save
  } catch (error) {
    console.error("Failed to save inline edit:", error);
  }
}

const teacherFields = [
  { label: "Phone Number", key: "phone_number", type: "string" },
  {
    label: "Teacher Info",
    key: "teacher_info",
    children: [
      { label: "Lecturer ID", key: "teacher_info.lecturer_id", type: "string" },
      {
        label: "Lecturer Name",
        key: "teacher_info.lecturer_name",
        type: "string",
      },
      {
        label: "Subjects",
        key: "teacher_info.subjects",
        isArray: true,
        type: "string",
      },
      {
        label: "Created At",
        key: "teacher_info.created_at",
        isDate: true,
        type: "date",
      },
      {
        label: "Updated At",
        key: "teacher_info.updated_at",
        isDate: true,
        type: "date",
      },
    ],
  },
];

const studentFields = [
  { label: "Student ID", key: "student_info.student_id", type: "string" },
  { label: "Grade", key: "student_info.grade", type: "number" },
  {
    label: "Class IDs",
    key: "student_info.class_ids",
    isArray: true,
    type: "string ",
  },
  { label: "Major", key: "student_info.major" },
  {
    label: "Birth Date",
    key: "student_info.birth_date",
    isDate: true,
    type: "date",
  },
  { label: "Batch", key: "student_info.batch", type: "string" },
  { label: "Address", key: "student_info.address" },
  { label: "Phone Number", key: "student_info.phone_number" },
  { label: "Email", key: "student_info.email", type: "email" },
  {
    label: "Attendance Record",
    key: "student_info.attendance_record",
    type: "dict",
    isDict: true,
  }, // might want special UI for this
  {
    label: "Courses Enrolled",
    key: "student_info.courses_enrolled",
    isArray: true,
    type: "string",
  },
  {
    label: "Scholarships",
    key: "student_info.scholarships",
    isArray: true,
    type: "string",
  },
  { label: "Current GPA", key: "student_info.current_gpa", type: "float" },
  {
    label: "Remaining Credits",
    key: "student_info.remaining_credits",
    type: "float",
  },
  {
    label: "Created At",
    key: "student_info.created_at",
    isDate: true,
    type: "date",
  },
  {
    label: "Updated At",
    key: "student_info.updated_at",
    isDate: true,
    type: "date",
  },
];

const adminFields = [
  { label: "Phone Number", key: "phone_number", type: "string" },
  { label: "Admin ID", key: "admin_id", type: "string" },
  { label: "Created At", key: "created_at", isDate: true, type: "date" },
  { label: "Updated At", key: "updated_at", isDate: true, type: "date" },
];

function updateUser(userId: string, flatData: Record<string, any>) {
  const nestedData = unflatten(flatData);
  const finalData = convertDatesToISOString(nestedData);

  userService.editUserDetail(userId, finalData);
}

function cancelEditDetail(key: string) {
  console.log(key);
}
function buildRoleUpdate(role: string, key: string, value: any) {
  const flatObj = { [key]: value };
  return unflatten(flatObj);
}

function getValueByKey(obj: any, key: string) {
  if (!obj || !key) return null;
  // Support nested keys with dot notation
  return key.split(".").reduce((acc, k) => acc?.[k], obj);
}
const userInfo = computed(() => {
  return userDetails.value?.profile?.role === "teacher"
    ? userDetails.value?.teacher_info
    : userDetails.value?.profile?.role === "student"
      ? userDetails.value?.student_info
      : userDetails.value?.profile;
});

const roleFields = computed(() => {
  if (userDetails.value?.profile?.role === "teacher") return teacherFields;
  if (userDetails.value?.profile?.role === "student") return studentFields;
  return adminFields;
});

const checkIsEditable = (key: string) => {
  return !key.endsWith("created_at") && !key.endsWith("updated_at");
};
const defaultDate = new Date();
defaultDate.setFullYear(defaultDate.getFullYear() - 18);
</script>

<template>
  <el-skeleton
    v-show="loading"
    :rows="10"
    animated
    border
    class="h-full"
    :loading="loading"
  />

  <el-table
    v-show="!loading"
    :data="pagedUsers"
    class="w-100% mt-4"
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
    "
  >
    <el-table-column fixed="left" label="Username" width="250" align="left">
      <template #default="{ row }">
        <MultiTypeEditCell
          v-model="row.username"
          label="username"
          @save="submitInlineEdit(row)"
          @cancel="cancelEdit(row, 'username')"
        />
      </template>
    </el-table-column>

    <el-table-column label="Email" width="250" align="left">
      <template #default="{ row }">
        <MultiTypeEditCell
          :placeholder="row.email || 'No email provided'"
          v-model="row.email"
          label="email"
          type="email"
          :disabled="false"
          @save="submitInlineEdit(row)"
          @cancel="cancelEdit(row, 'email')"
        />
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
      @current-change="handlePageChange"
    />
  </div>

  <div>
    <UserDetailDialog
      v-model="showDialog"
      :loading="dialogLoading"
      :title="userDetails?.profile?.role"
      :infoObject="userInfo"
      :fields="roleFields"
    >
      <template #custom="{ item, value, infoObject, fields }">
        <MultiTypeEditCell
          :model-value="value"
          :disabled="!checkIsEditable(item.key) || item.isDict"
          :type="item.type"
          :readonly="!checkIsEditable(item.key)"
          :dateDefaultVal="
            item.isDate
              ? new Date(new Date().setFullYear(new Date().getFullYear() - 18))
              : undefined
          "
          :infoObject="userInfo"
          :fields="fields"
          :label="item.label"
          @save="
            (val) => {
              updateUser(
                userDetails?.profile?.id,
                buildRoleUpdate(userDetails?.profile?.role, item.key, val)
              );
            }
          "
          @cancel="cancelEditDetail(item.key)"
        />
      </template>
    </UserDetailDialog>
  </div>
</template>

<style>
.compact-btn {
  padding: 0 4px !important;
  min-width: 0 !important;
  margin: 0 !important;
}
</style>
