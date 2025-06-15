import type { User } from "@/types/user";
import type { Role } from "@/types/role";
import type { AuthUser } from "@/types/auth";
import type { Teacher } from "@/types/models/Teacher";
import type { Student } from "@/types/models/Student";
import type { AxiosInstance } from "axios";

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
  getAuthUserDetails(id: string): Promise<AuthUser>;
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

export type UserDetail =
  | (User & { role: "teacher"; teacher: Teacher })
  | (User & { role: "student"; student: Student })
  | (User & { role: "admin"; admin_info: AuthUser });
