<script setup lang="ts">
import MultiTypeEditCell from "~/components/TableEdit/MultiTypeEditCell.vue";
import { defineProps, defineEmits, computed, useSlots } from "vue";
import { formatDate } from "~/utils/formatDate";
import type { InputType } from "~/constants/fields/types/field";
import { InputTypeEnum } from "~/constants/fields/types/field";

interface Row {
  username: string;
  email: string;
  role: string;
  createdAt: Date;
}

const props = defineProps<{
  label: string;
  field: keyof Row;
  fieldsSchema?: { type: InputType | string; readonly?: boolean };
  width?: number | string;
  align?: string;
  placeholder?: string;
  disabled?: boolean;
}>();
const emit = defineEmits(["save", "cancel", "edit"]);
const slots = useSlots();

const label = computed(() => props.label);
const field = computed(() => props.field);
const width = computed(() => props.width ?? 250);
const align = computed(() => props.align ?? "left");
const placeholder = computed(() => props.placeholder ?? "");
const type = computed(() => props.fieldsSchema?.type ?? InputTypeEnum.String);
const disabled = computed(() => props.disabled ?? false);
const readOnlyProp = computed(() => props.fieldsSchema?.readonly ?? false);

const TYPE_DATE = InputTypeEnum.Date;
</script>

<template>
  <el-table-column :label="label" :width="width" :align="align">
    <template #default="{ row }">
      <template v-if="$slots.cell">
        <slot name="cell" :row="row" :field="field" />
      </template>

      <template v-else-if="type === TYPE_DATE && readOnlyProp">
        <span>{{ formatDate(row[field]) }}</span>
      </template>

      <template v-else>
        <MultiTypeEditCell
          :default="row[field]"
          v-model="row[field]"
          :label="field"
          :type="type as InputType"
          :placeholder="placeholder"
          :disabled="disabled"
          :readonly="readOnlyProp"
          @save="$emit('save', row, field)"
          @cancel="$emit('cancel', row, field)"
        />
      </template>
    </template>
  </el-table-column>
</template>
