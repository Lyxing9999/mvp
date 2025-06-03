import type {
  ClassModel as IClassModel,
  ClassInfo,
} from "~/types/models/Class";
import type { ScheduleItem } from "~/types/models/Schedule";

export class ClassInfoModel implements ClassInfo {
  course_code = "";
  course_title = "";
  lecturer = "";
  email?: string;
  phone_number = "";
  hybrid = false;
  schedule?: ScheduleItem[];
  credits = 0;
  link_telegram?: string;
  department = "";
  description = "";
  year = new Date().getFullYear();

  constructor(data: Partial<ClassInfo> = {}) {
    Object.assign(this, { ...this, ...data });
  }
}

export class ClassModel implements IClassModel {
  _id?: string;
  class_id: string;
  class_info: ClassInfoModel;
  students_enrolled: string[] = [];
  max_students = 30;
  created_at: string;
  update_history: string[] = [];

  constructor(data: Partial<IClassModel> = {}) {
    this._id = data._id;
    this.class_id = data.class_id ?? crypto.randomUUID();
    this.class_info = new ClassInfoModel(data.class_info);
    this.students_enrolled = data.students_enrolled ?? [];
    this.max_students = data.max_students ?? 30;
    this.created_at = data.created_at ?? new Date().toISOString();
    this.update_history = data.update_history ?? [];
  }

  recordUpdate() {
    this.update_history.push(new Date().toISOString());
  }

  toDict(): Record<string, any> {
    const { recordUpdate, toDict, ...rest } = this;
    return rest;
  }
}
