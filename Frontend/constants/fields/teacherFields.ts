import type { Field } from "./types/Field";
export const teacherFields: Field[] = [
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
