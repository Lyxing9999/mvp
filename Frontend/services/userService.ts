import { useNuxtApp } from "#imports";
import type { User } from "@/types/user";
import type { Role } from "@/types/role";
import type { UserDetail } from "@/types/userServiceInterface";
export class UserService {
  private $api = useNuxtApp().$api;
  private baseURL = "/api/admin/";

  async listUsers(): Promise<User[]> {
    const res = await this.$api.get<{ data: User[] }>(this.baseURL);
    return res.data.data;
  }

  async getUserDetails(id: string): Promise<UserDetail> {
    const res = await this.$api.get<{ data: UserDetail }>(
      `${this.baseURL}users/detail/${id}`
    );
    return res.data.data;
  }


  async createUser(userData: any) {
    const res = await this.$api.post(`users/${this.baseURL}`, userData);
    return res.data.data;
  }

  async updateUser(id: string, userData: any) {
    const res = await this.$api.put(`users/${this.baseURL}${id}`, userData);
    return res.data.data;
  }

  async deleteUser(id: string) {
    const res = await this.$api.delete(`${this.baseURL}${id}`);
    return res.data.data;
  }

  async countByRole(): Promise<Record<Role, number>> {
    const res = await this.$api.get<{ data: Record<string, number> }>(
      `${this.baseURL}users/count-by-role`
    );
    return res.data.data as Record<Role, number>;
  }

  async compareGrowthStatsByRole(
    dates: Record<string, string | number>
  ): Promise<Record<string, number>> {
    const res = await this.$api.get<{ data: Record<string, number> }>(
      `${this.baseURL}users/growth-stats-by-role`,
      {
        params: dates,
      }
    );
    return res.data.data;
  }
}
