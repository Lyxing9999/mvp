<script lang="ts" setup>
import { ref, onMounted, computed, defineAsyncComponent, watch } from "vue";
import { UserModel } from "~/models/userModel";
import MultiTypeEditCell from "~/components/TableEdit/MultiTypeEditCell.vue";
import { unflatten } from "~/utils/unflatten";
import { adminFields } from "~/constants/fields/adminFields";
import { teacherFields } from "~/constants/fields/teacherFields";
import { studentFields } from "~/constants/fields/studentFields";
import { useUserStore } from "~/stores/userStore";
import { UserService } from "~/services/userService";
import AdminAttendanceDict from "~/components/admin/AdminAttendanceDict.vue";
const userService = new UserService();
import type { User } from "~/types/models/User";
import type { UserInfo, UserDetail } from "~/types/userServiceInterface";
import { useMessage } from "~/composables/common/useMessage";
import CustomButton from "~/components/Base/CustomButton.vue";
import CreateUserForm from "~/components/admin/CreateUserForm.vue";
import { CreateUserFormInput } from "~/types/userServiceInterface";
import EditableColumn from "~/components/TableEdit/EditableColumn.vue";
import type { AttendanceStatus } from "~/types/models/Attendance";
import { UserStoreError } from "~/errors/UserStoreError";
const UserDetailDialog = defineAsyncComponent(
  () => import("~/components/TableEdit/UserDetailDialog.vue")
);
const loading = ref(false);
const showDialog = ref(false);
const showCreateUserDialog = ref(false);
const userDetails = ref<UserDetail | null>(null);
const dialogLoading = ref(false);
const currentPage = ref(1);
const pageSize = ref(20);
const hasDraft = ref(false);
const userStore = useUserStore();
const { showSuccess, showInfo, showError } = useMessage();
const dialogKey = ref(0);

onMounted(async () => {
  await userStore.fetchUsers();
});

const saveId = ref<string | null>(null);

function cancelEdit(row: UserModel, field: CreateUserFormInput) {
  if (field === CreateUserFormInput.Username) {
    row.username = originalValue.value.username ?? row.username;
  } else if (field === CreateUserFormInput.Email) {
    row.email = originalValue.value.email ?? row.email;
  }
  editing.value = { id: null, field: null };
}

async function handleDelete(user: User) {
  try {
    await userService.deleteUser(user._id);
    showSuccess("User deleted successfully");
    userStore.fetchUsers();
  } catch (error) {
    if (error instanceof UserStoreError) {
      switch (error.code) {
        case "DELETE_USER_FAILED":
          showError(error.message);
          break;
        default:
          showError(error?.message || "Failed to delete user");
      }
    } else {
      showError((error as any)?.message || "Failed to delete user");
    }
  }
}

const editing = ref<{ id: string | null; field: CreateUserFormInput | null }>({
  id: null,
  field: null,
});
const originalValue = ref<{ username?: string; email?: string }>({});
async function submitInlineEdit(row: UserModel) {
  try {
    await userService.updateUser(row._id, {
      username: row.username,
      email: row.email,
    });
    editing.value = { id: null, field: null };
    showSuccess("User updated successfully");
    userStore.fetchUsers();
  } catch (error) {
    showError("Failed to save inline edit");
  }
}
function cancelEditDetail(key: string) {
  showInfo(`Cancel edit detail ${key}`);
}
function buildRoleUpdate(key: string, value: any) {
  const flatObj = { [key]: value };
  return unflatten(flatObj);
}

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

function isStudent(
  user: UserDetail
): user is Extract<UserDetail, { profile: { role: "student" } }> {
  return user?.profile?.role === "student";
}
function isTeacher(
  user: UserDetail
): user is Extract<UserDetail, { profile: { role: "teacher" } }> {
  return user.profile.role === "teacher";
}
function isAdmin(
  user: UserDetail
): user is Extract<UserDetail, { profile: { role: "admin" } }> {
  return user.profile.role === "admin";
}

const userInfo = computed(() => {
  if (!userDetails.value) return;
  if (isStudent(userDetails.value)) return userDetails.value.student_info;
  if (isTeacher(userDetails.value)) return userDetails.value.teacher_info;
  if (isAdmin(userDetails.value)) return userDetails.value.admin_info;
});

async function handleDetail(id: string) {
  try {
    dialogLoading.value = true;
    showDialog.value = false;
    dialogKey.value++;
    userDetails.value = null;
    saveId.value = id;
    const data = await userService.getUserDetails(id);
    userDetails.value = JSON.parse(JSON.stringify(data));
    showDialog.value = true;
  } catch (err) {
    showError("Failed to fetch user details");
  } finally {
    dialogLoading.value = false;
  }
}

async function handleInlineEditSubmitDialog(val: any, key: string) {
  if (!userInfo.value) return;

  const userId = userDetails.value?.profile?.id;
  if (!userId) {
    showError("User ID is not found");
    return;
  }
  try {
    await userStore.updateUserPatch(userId, buildRoleUpdate(key, val));
  } catch (error) {
    if (error instanceof UserStoreError) {
      showError(error.message);
    } else {
      showError("Failed to update user");
    }
  }
  try {
    const data = await userService.getUserDetails(saveId.value as string);
    userDetails.value = JSON.parse(JSON.stringify(data));
    await userStore.fetchUsers();
    showSuccess("User updated successfully");
  } catch (error) {
    if (error instanceof UserStoreError) {
      showError(error.message);
    } else {
      showError("Failed to fetch user details");
    }
  }
}

const attendance = computed({
  get(): Record<string, AttendanceStatus> {
    if (userDetails.value !== null && isStudent(userDetails.value)) {
      return (
        userDetails.value.student_info.student_info.attendance_record ?? {}
      );
    }
    return {};
  },
  set(newVal: Record<string, AttendanceStatus>) {
    if (userDetails.value !== null && isStudent(userDetails.value)) {
      userDetails.value.student_info.student_info.attendance_record = newVal;
    }
  },
});

function onAttendanceSave(updatedAttendance: Record<string, AttendanceStatus>) {
  handleInlineEditSubmitDialog(
    updatedAttendance,
    "student_info.attendance_record"
  );
}

const showCreateUserForm = () => {
  showCreateUserDialog.value = true;
};

const roleMap = {
  admin: { type: "info", label: "Admin" },
  teacher: { type: "primary", label: "Teacher" },
  student: { type: "success", label: "Student" },
};
const fieldsSchema = {
  username: { type: "string" },
  email: { type: "email" },
  role: { type: "string" },
  createdAt: { type: "date", readonly: true },
};

const users = computed(() => {
  return userStore.users;
});
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
  <CustomButton type="primary" @click="showCreateUserForm">
    Create User
  </CustomButton>
  <el-row class="mt-4" :gutter="20">
    <el-col :span="24" class="w-100%">
      <el-table v-show="!loading" :data="users" class="w-100% mt-4">
        <EditableColumn
          label="Username"
          field="username"
          :fieldsSchema="fieldsSchema.username"
          :type="fieldsSchema.username.type"
          @save="submitInlineEdit"
          @cancel="cancelEdit"
        />

        <EditableColumn
          label="Email"
          field="email"
          :disabled="true"
          :fieldsSchema="fieldsSchema.email"
          :type="fieldsSchema.email.type"
          @save="submitInlineEdit"
          @cancel="cancelEdit"
        />

        <EditableColumn
          label="Role"
          field="role"
          :fieldsSchema="fieldsSchema.role"
          :type="fieldsSchema.role.type"
          @save="submitInlineEdit"
          align="center"
          @cancel="cancelEdit"
        >
          <template #cell="{ row, field }">
            <el-tag
              :type="roleMap[row[field] as keyof typeof roleMap]?.type as any"
              class="w-100% !text-center"
            >
              {{ roleMap[row[field] as keyof typeof roleMap]?.label }}
            </el-tag>
          </template>
        </EditableColumn>

        <EditableColumn
          label="Created At"
          field="createdAt"
          :fieldsSchema="fieldsSchema.createdAt"
          :type="fieldsSchema.createdAt.type"
          @save="submitInlineEdit"
          @cancel="cancelEdit"
        />

        <el-table-column
          fixed="right"
          label="Operations"
          min-width="140"
          align="center"
          header-align="center"
        >
          <template #default="{ row }">
            <div class="flex justify-center items-center w-full">
              <div class="flex gap-2 max-w-[270px]">
                <CustomButton
                  type="success"
                  link
                  class="!bg-transparent !border-none"
                  @click="handleDetail(row._id)"
                >
                  Detail
                </CustomButton>
                <CustomButton
                  type="danger"
                  class="!bg-transparent !border-none"
                  link
                  @click="handleDelete(row)"
                >
                  Delete
                </CustomButton>
              </div>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-col>
  </el-row>

  <el-empty v-if="!loading && users.length === 0" description="No users found.">
    <template #image>
      <el-icon><User /></el-icon>
    </template>
  </el-empty>

  <div class="flex justify-end mt-4">
    <el-pagination
      background
      layout="prev, pager, next"
      :total="users.length"
      :page-size="pageSize"
      :current-page="currentPage"
    />
  </div>

  <div class="mt-4">
    <UserDetailDialog
      v-model="showDialog"
      destroy-on-close
      :loading="dialogLoading"
      :key="dialogKey"
      :title="userDetails?.profile?.role as string"
      :infoObject="userInfo as UserInfo"
      :fields="roleFields as any"
      width="800px !important"
    >
      <template #custom="{ item, value, fields }">
        <MultiTypeEditCell
          :model-value="value"
          :default="value"
          :type="item.type || 'string'"
          @info="(msg) => showInfo(msg)"
          :readonly="!checkIsEditable(item.key)"
          :disabled="!checkIsEditable(item.key)"
          :dateDefaultVal="
            item.isDate
              ? new Date(new Date().setFullYear(new Date().getFullYear() - 18))
              : undefined
          "
          :infoObject="value"
          :fields="fields"
          :label="item.label"
          @save="(val) => handleInlineEditSubmitDialog(val, item.key)"
          @cancel="cancelEditDetail(item.key)"
        >
          <template #dict="{ disabled, label, placeholder }">
            <AdminAttendanceDict
              v-model:modelValue="attendance"
              v-model:draft="hasDraft"
              :disabled="disabled"
              :label="label"
              :placeholder="placeholder"
              :key="item.key"
              @save="
                (v) => onAttendanceSave(v as Record<string, AttendanceStatus>)
              "
            />
          </template>
        </MultiTypeEditCell>
      </template>
    </UserDetailDialog>
  </div>
  <div class="mt-4">
    <el-dialog
      v-model="showCreateUserDialog"
      title="Create User"
      width="500px !important"
      destroy-on-close
    >
      <CreateUserForm
        @created="showCreateUserDialog = false"
        @error="showError"
      />
    </el-dialog>
  </div>
</template>

<style>
.compact-btn {
  padding: 0 4px !important;
  min-width: 0 !important;
  margin: 0 !important;
}
</style>
