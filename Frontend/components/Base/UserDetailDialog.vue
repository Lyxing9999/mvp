<script lang="ts" setup>
import { computed, defineProps } from "vue";
import { formatDate } from "~/utils/formatDate";
import type { UserDetail } from "~/types/userServiceInterface";
import { Role } from "~/types/models/User";

const props = defineProps<{
  modelValue: boolean;
  loading: boolean;
  userDetails: UserDetail | null;
}>();

const emit = defineEmits<{
  (event: "update:modelValue", value: boolean): void;
}>();

const dialogTitle = computed(() => {
  const role = props.userDetails?.profile?.role;
  if (role === Role.Admin) return "Admin Details";
  if (role === Role.teacher) return "Teacher Details";
  if (role === Role.student) return "Student Details";
  return "User Details";
});
</script>

<template>
  <el-dialog
    :model-value="modelValue"
    :title="dialogTitle"
    width="50%"
    @close="emit('update:modelValue', false)">
    <el-skeleton :loading="loading" animated>
      <template v-if="userDetails?.profile?.role === 'teacher'">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Phone Number">
            {{ userDetails.teacher_info?.phone_number || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Lecturer ID">
            {{ userDetails.teacher_info?.teacher_info?.lecturer_id || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Lecturer Name">
            {{ userDetails.teacher_info?.teacher_info?.lecturer_name || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Subjects">
            {{
              userDetails.teacher_info?.teacher_info?.subjects?.join(", ") ||
              "N/A"
            }}
          </el-descriptions-item>
          <el-descriptions-item label="Created At">
            {{ formatDate(userDetails.teacher_info?.created_at) || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Updated At">
            {{ formatDate(userDetails.teacher_info?.updated_at) || "N/A" }}
          </el-descriptions-item>
        </el-descriptions>
      </template>
      <template v-else-if="userDetails?.profile?.role === 'student'">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Student ID">
            {{ userDetails.student_info?.student_id || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Year Level">
            {{ userDetails.student_info?.year_level || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Major">
            {{ userDetails.student_info?.major || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Batch">
            {{ userDetails.student_info?.batch || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Class IDs">
            {{ userDetails.student_info?.class_ids?.join(", ") || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Courses Enrolled">
            {{ userDetails.student_info?.courses_enrolled?.length || 0 }}
            course(s)
          </el-descriptions-item>
          <el-descriptions-item label="Scholarships">
            {{ userDetails.student_info?.scholarships?.join(", ") || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Expected Graduation Year">
            {{ userDetails.student_info?.expected_graduation_year || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Current GPA">
            {{ userDetails.student_info?.current_gpa ?? "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Remaining Credits">
            {{ userDetails.student_info?.remaining_credits ?? "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Birth Date">
            {{ formatDate(userDetails.student_info?.birth_date) || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Phone Number">
            {{ userDetails.student_info?.phone_number || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Email">
            {{ userDetails.student_info?.email || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Address">
            {{ userDetails.student_info?.address || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Created At">
            {{ formatDate(userDetails.student_info?.createdAt) || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Updated At">
            {{ formatDate(userDetails.student_info?.updated_at) || "N/A" }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>Attendance Record</el-divider>
        <el-table
          :data="
            Object.entries(userDetails.student_info?.attendance_record || {})
          "
          border
          stripe
          size="small">
          <el-table-column prop="0" label="Date" />
          <el-table-column prop="1" label="Status" />
        </el-table>
      </template>

      <template v-else-if="userDetails?.profile?.role === 'admin'">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Phone Number">
            {{ userDetails.admin_info?.phone_number || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Admin ID">
            {{ userDetails.admin_info?.admin_id || "N/A" }}
          </el-descriptions-item>
          <el-descriptions-item label="Created At">
            {{ formatDate(userDetails.admin_info?.createdAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="Updated At">
            {{ formatDate(userDetails.admin_info?.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </template>
      <template v-else>
        <div class="text-center">No user details available.</div>
      </template>
    </el-skeleton>
  </el-dialog>
</template>
