import type { User } from "~/types/models/User";
import { Role } from "~/types/models/User";

export class UserModel implements User {
  _id?: string;
  role: Role;
  username: string;
  email?: string;
  password?: string;

  constructor(data: Partial<User> = {}) {
    this._id = data._id;
    this.role = data.role ?? Role.student;
    this.username = data.username?.trim() ?? "";
    this.email = data.email?.trim();
    this.password = data.password?.trim();
  }

  toDict(includePassword = false): Record<string, any> {
    const result: Record<string, any> = {
      role: this.role,
      username: this.username,
    };

    if (this._id) result._id = this._id;
    if (this.email) result.email = this.email;
    if (includePassword && this.password) result.password = this.password;

    return result;
  }
}
