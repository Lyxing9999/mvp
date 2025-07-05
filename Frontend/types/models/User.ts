export enum Role {
  teacher = "teacher",
  student = "student",
  Admin = "admin",
}


export interface User {
  _id: string;
  role: Role;
  username: string;
  email?: string;
  password?: string;
  createdAt?: string;
  created_at?: string;
}

