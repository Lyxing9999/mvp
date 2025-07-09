import type { User } from "~/types/models/User";
import type { AxiosInstance } from "axios";
import type { Teacher } from "~/types/models/Teacher";
import type { Student } from "~/types/models/Student";
import type { AuthUser as AuthUserType } from "~/types/auth";
import type { Student as StudentType } from "~/types/models/Student";
import type { Teacher as TeacherType } from "~/types/models/Teacher";
import type { User as UserType } from "~/types/models/User";

export interface UserServiceInterface {
  listUsers(): Promise<User[]>;
  getUserDetails(id: string): Promise<User>;
  createUser(userData: Partial<User>): Promise<User>;
  updateUser(id: string, userData: Partial<User>): Promise<User>;
  deleteUser(id: string): Promise<void>;
  countByRole(): Promise<Record<Role, number>>;
  compareGrowthStatsByRole(
    dates: Record<string, string | number>
  ): Promise<Record<string, number>>;
  getTeacherDetails(id: string): Promise<Teacher>;
  getStudentDetails(id: string): Promise<Student>;
  getAuthUserDetails(id: string): Promise<AuthUserType>;
  setApiClient(apiClient: AxiosInstance): void;
  getApiClient(): AxiosInstance;
  setBaseURL(baseURL: string): void;
  getBaseURL(): string;
  getUserByUsername(username: string): Promise<User | null>;
  getUserByEmail(email: string): Promise<User | null>;
  getUserById(id: string): Promise<User | null>;
  getTeacherById(id: string): Promise<Teacher | null>;
  getStudentById(id: string): Promise<Student | null>;
  getAuthUserById(id: string): Promise<AuthUser | null>;
  getUserByPhoneNumber(phoneNumber: string): Promise<User | null>;
  getTeacherByPhoneNumber(phoneNumber: string): Promise<Teacher | null>;
  getStudentByPhoneNumber(phoneNumber: string): Promise<Student | null>;
  getAuthUserByPhoneNumber(phoneNumber: string): Promise<AuthUser | null>;
  getUsersByRole(role: Role): Promise<User[]>;
  getTeachersByRole(role: Role): Promise<Teacher[]>;
  getStudentsByRole(role: Role): Promise<Student[]>;
  getAuthUsersByRole(role: Role): Promise<AuthUser[]>;
  getUsersByCreatedAt(date: string): Promise<User[]>;
}
export interface UserServiceConstructor {
  new (): UserServiceInterface;
}

export type Role = "student" | "teacher" | "admin";

export type Profile = {
  id: string;
  username: string;
  role: Role;
  email: string | null;
  created_at: string;
  updated_at: string | null;
};

export type StudentInfo = {
  id: string;
  user_id: string;
  student_info: {
    class_ids: string[];
    batch: string;
    birth_date: string;
    address: string;
    attendance_record: any;
    created_at: string;
    updated_at?: string;
  };
};

export type TeacherInfo = {
  id: string;
  user_id: string;
  phone_number: string;
  teacher_info: {
    lecturer_id: string;
    lecturer_name: string;
    subjects: string[];
    created_at: string;
    updated_at?: string;
  };
};

export type AuthUser = {
  id: string;
  user_id: string;
  admin_info: {
    permission_level: string;
    created_at: string;
    updated_at?: string;
  };
};
export type UserInfo = StudentType | TeacherType | AuthUserType;

export type UserDetail =
  | { profile: Profile & { role: "student" }; student_info: StudentType }
  | { profile: Profile & { role: "teacher" }; teacher_info: TeacherType }
  | { profile: Profile & { role: "admin" }; admin_info: AuthUserType };

export type UserFormInput = {
  username: string;
  email?: string;
  password: string;
  role: string;
};

export enum CreateUserFormFields {
  Username = "username",
  Email = "email",
  Password = "password",
  Role = "role",
}
