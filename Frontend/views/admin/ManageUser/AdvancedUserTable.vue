<script lang="ts" setup>
import { ref, onMounted, defineAsyncComponent, computed } from "vue";
import MultiTypeEditCell from "~/components/TableEdit/MultiTypeEditCell.vue";
import { useUserStore } from "~/stores/userStore";
import AdminAttendanceDict from "~/components/admin/AdminAttendanceDict.vue";
import CustomButton from "~/components/Base/CustomButton.vue";
import CreateUserForm from "~/components/admin/CreateUserForm.vue";
import type { AttendanceStatus } from "~/types/models/Attendance";
import { useUsersManage } from "~/composables/useUsersManage";
import { userFieldsSchema } from "~/constants/fields/userFieldConfig";
import SmartTable from "~/components/TableEdit/SmartTable.vue";
import type { User } from "~/types/models/User";

const {
  showCreateUserDialog,
  showDialog,
  dialogLoading,
  dialogKey,
  currentPage,
  pageSize,
  hasDraft,
  userDetails,
  cancelEdit,
  handleDelete,
  submitInlineEdit,
  handleDetail,
  handleInlineEditSubmitDialog,
  showCreateUserForm,
  userInfo,
  roleFields,
  attendance,
  onAttendanceSave,
  checkIsEditable,
  cancelEditDetail,
  showInfo,
  showError,
} = useUsersManage();

const UserDetailDialog = defineAsyncComponent(
  () => import("~/components/TableEdit/UserDetailDialog.vue")
);

const userStore = useUserStore();
const loading = ref(false);

onMounted(async () => {
  loading.value = true;
  try {
    await userStore.fetchUsers();
  } finally {
    loading.value = false;
  }
});

const users = computed<User[]>(() => userStore.users);
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
      <SmartTable
        :data="users"
        :columns="userFieldsSchema"
        @save="submitInlineEdit"
      >
        <template #operation="{ row }">
          <el-button type="primary" @click="handleDetail(row)" size="small">
            Detail
          </el-button>

          <el-popconfirm
            title="Are you sure to delete this user?"
            @confirm="handleDelete(row)"
          >
            <template #reference>
              <el-button type="danger" size="small">Delete</el-button>
            </template>
          </el-popconfirm>
        </template>
      </SmartTable>
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
      :title="userDetails?.profile?.role ?? ''"
      :infoObject="userInfo as Record<string, any>"
      :fields="roleFields"
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
              @save="(v) => onAttendanceSave(v as Record<string, AttendanceStatus>)"
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
