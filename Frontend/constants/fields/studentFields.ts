import type { Field } from './types/field';

export const studentFields: Field[] = [
  { label: "Student ID", key: "student_info.student_id", type: "string" },
  { label: "Grade", key: "student_info.grade", type: "number" },
  {
    label: "Class IDs",
    key: "student_info.class_ids",
    isArray: true,
    type: "string",

  },
  { label: "Major", key: "student_info.major", type: "string" },
  { label: "Birth Date", key: "student_info.birth_date", isDate: true, type: "date" },
  { label: "Batch", key: "student_info.batch", type: "string" },
  { label: "Address", key: "student_info.address", type: "string" },
  { label: "Phone Number", key: "student_info.phone_number", type: "string" },
  { label: "Email", key: "student_info.email", type: "email" },
  {
    label: "Attendance Record",
    key: "student_info.attendance_record",
    isDict: true,
    type: "dict",
  },
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
  { label: "Remaining Credits", key: "student_info.remaining_credits", type: "float" },
  { label: "Created At", key: "student_info.created_at", isDate: true, type: "date" },
  { label: "Updated At", key: "student_info.updated_at", isDate: true, type: "date" },
];
