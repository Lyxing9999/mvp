export enum InputTypeEnum {
  Number = "number",
  Float = "float",
  Date = "date",
  String = "string",
  Email = "email",
  Dict = "dict",
  Operation = "operation",
}

export type InputType = `${InputTypeEnum}`;

export interface Field {
  label: string;
  key: string;
  children?: Field[];
  format?: string;
  type?: InputType;
  isArray?: boolean;
  isDate?: boolean;
  isDict?: boolean;
}
