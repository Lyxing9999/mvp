export interface TeacherInfo {
  teacher_id: string;
  lecturer_name?: string;
  subjects: string[];
  created_at: string;
  updated_at?: string;
}

export interface Teacher {
  _id?: string;
  user_id: string;
  phone_number?: string;
  teacher_info: TeacherInfo;
}
