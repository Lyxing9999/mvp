import { useNuxtApp, useRuntimeConfig, useRouter } from "#imports";
import { ElMessage } from "element-plus";
import type { AuthUser } from "~/types/auth";
import { UserModel } from "~/models/userModel";

// Define roles for type safety
export enum UserRole {
  Admin = "admin",
  Teacher = "teacher",
  Student = "student",
}

interface LoginResponse {
  user: AuthUser;
  access_token: string;
}

export class AuthService {
  private $api = useNuxtApp().$api;
  private router = useRouter();
  private config = useRuntimeConfig();

  async login(form: { username: string; password: string }) {
    if (!form.username || !form.password) {
      ElMessage.warning("Please fill in all fields");
      return;
    }

    try {
      const res = await this.$api.post<LoginResponse>("/auth/login", form);

      if (!res?.data) {
        ElMessage.error("No data from server");
        return;
      }

      const userData = res.data.user;
      const token = res.data.access_token;

      if (!userData || !token) {
        ElMessage.error("Invalid response from server");
        return;
      }

      // Store token
      this.storeToken(token);

      // Instantiate user model
      const user = new UserModel(userData);

      console.log("Logged in user:", user.toDict());

      // Redirect according to user role
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
    this.clearToken();
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
