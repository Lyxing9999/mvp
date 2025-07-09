// composables/useUsersManage.ts
import { ref, computed, onMounted } from "vue";
import { useUserStore } from "~/stores/userStore";
import { UserService } from "~/services/userService";
import { unflatten } from "~/utils/unflatten";
import type { UserDetail } from "~/types/userServiceInterface";
import { CreateUserFormFields } from "~/types/userServiceInterface";
import { UserStoreError } from "~/errors/UserStoreError";
import { useMessage } from "~/composables/common/useMessage";
import { adminFields } from "~/constants/fields/adminFields";
import type { User } from "~/types/models/User";
import { teacherFields } from "~/constants/fields/teacherFields";
import { studentFields } from "~/constants/fields/studentFields";
import type { AttendanceStatus } from "~/types/models/Attendance";

export function useUsersManage() {
  const userStore = useUserStore();
  const userService = new UserService();
  const { showSuccess, showError, showInfo } = useMessage();

  const showDialog = ref(false);
  const showCreateUserDialog = ref(false);
  const userDetails = ref<UserDetail | null>(null);
  const dialogLoading = ref(false);
  const dialogKey = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(20);
  const hasDraft = ref(false);
  const saveId = ref<string | null>(null);

  const editing = ref<{
    id: string | null;
    field: CreateUserFormFields | null;
  }>({
    id: null,
    field: null,
  });

  const originalValue = ref<{ username?: string; email?: string }>({});

  // Computed users from store
  const users = computed(() => userStore.users);

  // Role-based fields
  const roleFields = computed(() => {
    if (userDetails.value?.profile?.role === "teacher") return teacherFields;
    if (userDetails.value?.profile?.role === "student") return studentFields;
    return adminFields;
  });

  // Check if field editable (ignore created_at and updated_at)
  const checkIsEditable = (key: string) => {
    return !key.endsWith("created_at") && !key.endsWith("updated_at");
  };

  // Role type guards
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

  // User info based on role
  const userInfo = computed(() => {
    if (!userDetails.value) return;
    if (isStudent(userDetails.value)) return userDetails.value.student_info;
    if (isTeacher(userDetails.value)) return userDetails.value.teacher_info;
    if (isAdmin(userDetails.value)) return userDetails.value.admin_info;
  });

  // Attendance for student
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

  // Load users on mounted
  onMounted(async () => {
    await userStore.fetchUsers();
  });

  // Cancel inline edit: revert changes
  function cancelEdit(row: any, field: CreateUserFormFields) {
    if (field === CreateUserFormFields.Username) {
      row.username = originalValue.value.username ?? row.username;
    } else if (field === CreateUserFormFields.Email) {
      row.email = originalValue.value.email ?? row.email;
    }
    editing.value = { id: null, field: null };
  }

  // Delete user
  async function handleDelete(user: User) {
    try {
      await userService.deleteUser(user._id);
      showSuccess("User deleted successfully");
      await userStore.fetchUsers();
    } catch (error) {
      if (error instanceof UserStoreError) {
        showError(error.message);
      } else {
        showError((error as any)?.message || "Failed to delete user");
      }
    }
  }

  // Submit inline edit
  async function submitInlineEdit(row: any, field: string) {
    console.log("this is row", row);
    console.log("this is field", field);
    try {
      await userService.updateUser(row._id, {
        username: row.username,
        email: row.email,
      });
      editing.value = { id: null, field: null };
      showSuccess("User updated successfully");
      await userStore.fetchUsers();
    } catch {
      showError("Failed to save inline edit");
    }
  }

  // Build update object for patch API (unflatten nested keys)
  function buildRoleUpdate(key: string, value: any) {
    const flatObj = { [key]: value };
    return unflatten(flatObj);
  }

  // Open user detail dialog and fetch details
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
    } catch {
      showError("Failed to fetch user details");
    } finally {
      dialogLoading.value = false;
    }
  }

  // Submit inline edit inside detail dialog
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

    // Refresh details and list
    try {
      const data = await userService.getUserDetails(saveId.value as string);
      userDetails.value = JSON.parse(JSON.stringify(data));
      await userStore.fetchUsers();
      showSuccess("User updated successfully");
    } catch {
      showError("Failed to fetch user details");
    }
  }

  // Save attendance (student only)
  function onAttendanceSave(
    updatedAttendance: Record<string, AttendanceStatus>
  ) {
    handleInlineEditSubmitDialog(
      updatedAttendance,
      "student_info.attendance_record"
    );
  }

  // Open create user dialog
  const showCreateUserForm = () => {
    showCreateUserDialog.value = true;
  };

  // Role label map (for UI badges etc)
  const roleMap = {
    admin: { type: "info", label: "Admin" },
    teacher: { type: "primary", label: "Teacher" },
    student: { type: "success", label: "Student" },
  } as const;

  const fieldsSchema = [
    { field: "username", label: "Username", type: "string" },
    { field: "email", label: "Email", type: "email" },
    { field: "role", label: "Role", type: "string" },
    { field: "createdAt", label: "Created At", type: "date", readonly: true },
  ];

  const cancelEditDetail = (key: string) => {
    console.log("cancelEditDetail", key);
  };

  return {
    showDialog,
    showCreateUserDialog,
    userDetails,
    dialogLoading,
    dialogKey,
    currentPage,
    pageSize,
    hasDraft,
    saveId,
    editing,
    originalValue,
    users,
    roleFields,
    userInfo,
    attendance,
    roleMap,
    fieldsSchema,
    cancelEdit,
    handleDelete,
    submitInlineEdit,
    handleDetail,
    handleInlineEditSubmitDialog,
    onAttendanceSave,
    showCreateUserForm,
    checkIsEditable,
    cancelEditDetail,
    showInfo,
    showError,
  };
}
