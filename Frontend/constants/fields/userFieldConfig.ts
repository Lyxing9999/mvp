import type { ColumnConfig } from "~/constants/fields/types/FieldConfig";
import type { User } from "~/types/models/User";
import { renderUserRole } from "~/constants/renders/roleTag";

export const userFieldsSchema: ColumnConfig<User>[] = [
  { field: "username", label: "Username", type: "string" },
  { field: "email", label: "Email", type: "email" },
  {
    field: "role",
    label: "Role",
    type: "string",
    readonly: true,
    showSaveCancelControls: false,
    render: (row) => renderUserRole(row),
  },
  {
    field: "createdAt",
    label: "Created At",
    type: "date",
    disabled: true,
    readonly: true,
  },
  {
    field: "actions" as keyof User,
    label: "Actions",
    type: "operation",
    slot: true,
  },
];
