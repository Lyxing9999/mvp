import type {
  ClassModel as IClassModel,
  ClassInfo,
} from "~/types/models/Class";
import type { ScheduleItem } from "~/types/models/Schedule";

export class ClassInfoModel implements ClassInfo {
  course_code: string = "";
  course_title: string = "";
  lecturer: string = "";
  email?: string;
  phone_number: string = "";
  hybrid: boolean = false;
  schedule?: ScheduleItem[];
  credits: number = 0;
  link_telegram?: string;
  department: string = "";
  description: string = "";
  year: number = new Date().getFullYear();

  constructor(data: Partial<ClassInfo> = {}) {
    Object.assign(this, {
      course_code: "",
      course_title: "",
      lecturer: "",
      phone_number: "",
      hybrid: false,
      credits: 0,
      department: "",
      description: "",
      year: new Date().getFullYear(),
      ...data,
    });
  }

  static empty(): ClassInfoModel {
    return new ClassInfoModel();
  }

  toDict(): Record<string, any> {
    return {
      course_code: this.course_code,
      course_title: this.course_title,
      lecturer: this.lecturer,
      email: this.email,
      phone_number: this.phone_number,
      hybrid: this.hybrid,
      schedule: this.schedule,
      credits: this.credits,
      link_telegram: this.link_telegram,
      department: this.department,
      description: this.description,
      year: this.year,
    };
  }
}

export class ClassModel implements IClassModel {
  _id?: string;
  class_id: string;
  class_info: ClassInfoModel;
  students_enrolled: string[] = [];
  max_students: number = 30;
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
  static empty(): ClassModel {
    return new ClassModel();
  }

  toDict(): Record<string, any> {
    return {
      _id: this._id,
      class_id: this.class_id,
      class_info: this.class_info.toDict(),
      students_enrolled: this.students_enrolled,
      max_students: this.max_students,
      created_at: this.created_at,
      update_history: this.update_history,
    };
  }
}
