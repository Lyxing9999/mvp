import { useNuxtApp, useRuntimeConfig, useRouter } from "#imports";
import { ElMessage } from "element-plus";
import type { AuthUser, LoginResponse } from "~/types/auth";
import { UserModel } from "~/models/userModel";
import { useAuthStore } from "~/stores/authStore";

// Define roles for type safety
export enum UserRole {
  Admin = "admin",
  Teacher = "teacher",
  Student = "student",
}

export class AuthService {
  private $api = useNuxtApp().$api;
  private router = useRouter();
  private config = useRuntimeConfig();
  private baseURL = "/api/auth/";
  async login(form: { username: string; password: string }) {
    if (!form.username || !form.password) {
      ElMessage.warning("Please fill in all fields");
      return;
    }

    try {
      const res = await this.$api.post<LoginResponse>(
        `${this.baseURL}login`,
        form
      );
      if (!res?.data) {
        ElMessage.error("No data from server");
        return;
      }

      const userData = res.data.data.user;
      const token = res.data.data.access_token;
      console.log(userData, token);
      if (!userData || !token) {
        ElMessage.error("Invalid response from server");
        return;
      }

      const authStore = useAuthStore();
      authStore.login(token, userData);

      const user = new UserModel(userData);
      console.log("Logged in user:", user.toDict());

      this.redirectByRole(user.role);
    } catch (err) {
      console.error("Login failed", err);
      ElMessage.error("Login failed, please try again");
    }
  }

  loginWithGoogle() {
    window.location.href = `${this.config.public.apiBase}/auth/google/login`;
  }

  logout() {
    const authStore = useAuthStore();
    this.clearToken();
    authStore.logout();
    this.router.push("/auth/login");
    ElMessage.success("Logged out successfully");
  }
  getToken(): string | null {
    return localStorage.getItem("token");
  }

  private storeToken(token: string) {
    localStorage.setItem("token", token);
  }

  private clearToken() {
    localStorage.removeItem("token");
  }

  private redirectByRole(role: string) {
    switch (role) {
      case UserRole.Admin:
        this.router.push("/admin/dashboard");
        break;
      case UserRole.Teacher:
        this.router.push("/teacher/dashboard");
        break;
      default:
        this.router.push("/student/dashboard");
    }
  }
}
