import { Role } from "~/types/models/User";
export interface StudentInfo {
  student_id: string;
  grade?: string;
  class_ids: string[];
  major?: string;
  birth_date?: string;
  batch?: string;
  address?: string;
  phone_number?: string;
  email?: string;
  attendance_record: Record<string, string>; // Use AttendanceStatus enum if declared
  courses_enrolled: string[];
  scholarships: string[];
  current_gpa: number;
  remaining_credits: number;
  created_at: string;
  updated_at?: string;
}

export interface Student {
  _id?: string;
  user_id: string;
  role: Role;
  username: string;
  email?: string;
  password?: string;
  student_info: StudentInfo;
}
