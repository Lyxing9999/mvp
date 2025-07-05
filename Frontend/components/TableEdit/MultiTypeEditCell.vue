<script setup lang="ts">
import { ref, computed, nextTick, watch } from "vue";
import type { InputType, InputTypeEnum } from "~/constants/fields/types/field";
import SaveCancelControls from "~/components/TableEdit/SaveCancelControls.vue";
import type { ElInput } from "element-plus";
const inputRef = ref<InstanceType<typeof ElInput> | null>(null);

interface TagObject {
  label: string;
  order?: number;
}

type ModelValue =
  | string
  | TagObject
  | string[]
  | number
  | Record<string, string>;

const props = defineProps<{
  modelValue: ModelValue;
  label: string;
  disabled?: boolean;
  type?: InputType;
  placeholder?: string;
  dateDefaultVal?: Date;
  isDate?: boolean;
  isDict?: boolean;
  readonly?: boolean;
  editable?: boolean;
  title?: string;
  confirmText?: string;
  cancelText?: string;
}>();

const emit = defineEmits([
  "update:modelValue",
  "save",
  "cancel",
  "info",
  "validate",
]);

const tags = ref<string[]>([]);
const showInputField = ref(false);
const isAddingTag = ref(false);

const isArray = computed(() => Array.isArray(props.modelValue));
const isDict = computed(
  () =>
    props.isDict &&
    props.modelValue !== null &&
    !Array.isArray(props.modelValue)
);
const isTag = computed(
  () =>
    typeof props.modelValue === "object" &&
    props.modelValue !== null &&
    !Array.isArray(props.modelValue) &&
    "label" in props.modelValue
);
const inputValue = ref<ModelValue | null>(null);

function getNormalizedValue(): ModelValue {
  if (isArray.value) return tags.value;
  if (isDict.value) return inputValue.value as Record<string, string>;
  if (isTag.value) {
    return {
      ...(props.modelValue as TagObject),
      label: inputValue.value?.toString() ?? "",
    };
  }
  return (inputValue.value ?? "") as ModelValue;
}

watch(
  () => props.modelValue,
  () => {
    const newVal = props.modelValue;

    if (Array.isArray(newVal)) {
      tags.value = newVal.map((item) =>
        typeof item === "string" ? item : (item as TagObject).label ?? ""
      );
      inputValue.value = "";
    } else if (isDict.value) {
      inputValue.value = { ...(newVal as Record<string, string>) };
      tags.value = [];
    } else if (typeof newVal === "number") {
      inputValue.value = newVal;
      tags.value = [];
    } else if (typeof newVal === "string") {
      inputValue.value = newVal;
      tags.value = [];
    } else if (isTag.value) {
      inputValue.value = (newVal as TagObject).label ?? "";
      tags.value = [];
    } else {
      inputValue.value = "";
      tags.value = [];
    }
  },
  { immediate: true }
);

function showInput() {
  showInputField.value = true;
}
function addTag() {
  const val = inputValue.value?.toString().trim();
  if (!val) return;

  if (tags.value.includes(val)) {
    emit("info", `"${val}" is already added and cannot be duplicated.`);
    emit("validate", false); // validation failed
    inputValue.value = "";
    isAddingTag.value = false;
    return;
  }
  emit("validate", true);
  tags.value.push(val);
  inputValue.value = "";
  isAddingTag.value = false;
}

function removeTag(index: number) {
  tags.value.splice(index, 1);
}

function submit() {
  const newValue = getNormalizedValue();
  emit("update:modelValue", newValue);
  emit("save", newValue);
  showInputField.value = false;
}

function cancel() {
  inputValue.value =
    typeof props.modelValue === "string"
      ? props.modelValue
      : (props.modelValue as TagObject)?.label ?? "";
  emit("cancel");
  showInputField.value = false;
  isAddingTag.value = false;
}

function handleDictUpdate(newValue: any) {
  inputValue.value = newValue;
  emit("update:modelValue", newValue);
}
watch(showInputField, (val) => {
  if (val) nextTick(() => inputRef.value?.focus());
});

function enableAddingTag() {
  isAddingTag.value = true;
  inputValue.value = "";
  nextTick(() => inputRef.value?.focus());
}
</script>

<template>
  <div>
    <template v-if="isArray">
      <div v-if="showInputField" class="flex flex-wrap gap-2 items-center">
        <el-tag
          v-for="(tag, i) in tags"
          :key="i"
          closable
          @close="removeTag(i)"
          size="small"
          :disabled="disabled"
          :readonly="readonly"
        >
          {{ tag }}
        </el-tag>

        <el-tag v-if="isAddingTag" class="px-0">
          <el-input
            ref="inputRef"
            v-model="inputValue as unknown as string | null"
            class="w-20"
            size="small"
            @keyup.enter="addTag"
            @blur="addTag"
            style="border: none; outline: none"
          />
        </el-tag>

        <el-tag
          tabindex="0"
          @keydown.enter.prevent="enableAddingTag"
          @click="enableAddingTag"
          type="info"
          class="cursor-pointer"
          :disabled="disabled"
          :readonly="readonly"
        >
          + {{ label }}
        </el-tag>

        <div class="mt-2 w-full flex justify-end gap-2">
          <SaveCancelControls @confirm="submit" @cancel="cancel" />
        </div>
      </div>

      <div
        v-else
        class="flex flex-wrap gap-2 cursor-pointer"
        @click="showInput"
      >
        <el-tag
          v-for="(tag, i) in tags"
          :key="i"
          closable
          @close.stop="removeTag(i)"
          size="small"
          :disabled="disabled"
          :readonly="readonly"
        >
          {{ tag }}
        </el-tag>
        <el-tag
          type="info"
          class="cursor-pointer"
          :disabled="disabled"
          :readonly="readonly"
        >
          + New Tag</el-tag
        >
      </div>
    </template>

    <template v-else>
      <div
        v-if="!showInputField"
        class="cursor-pointer flex justify-between items-center"
        @click="showInput()"
      >
        <span class="truncate max-w-[170px] block">{{
          inputValue || props.placeholder || "—"
        }}</span>
        <span v-if="!disabled" class="flex justify-end items-center space-x-1">
          <el-icon><Edit /></el-icon>
        </span>
      </div>
      <el-input-number
        v-else-if="type === 'number' || type === 'float'"
        v-model="inputValue as unknown as number | null"
        :disabled="disabled"
        :readonly="readonly"
        size="small"
        class="w-full"
        :placeholder="label"
      >
        <template #suffix>
          <SaveCancelControls @confirm="submit" @cancel="cancel" />
        </template>
      </el-input-number>
      <div v-else-if="type === 'date'">
        <el-date-picker
          v-model="inputValue as unknown as Date | undefined"
          :readonly="readonly"
          :disabled="disabled"
          size="small"
          class="w-full"
          :placeholder="label"
          :default-value="props.dateDefaultVal"
        />
        <div v-if="!disabled" class="flex items-center space-x-1">
          <SaveCancelControls @confirm="submit" @cancel="cancel" />
        </div>
      </div>

      <el-input
        v-else-if="type === 'email'"
        v-model="inputValue as unknown as string | null"
        type="email"
        size="small"
        class="w-full"
        :placeholder="label"
        :disabled="disabled"
        :readonly="readonly"
      >
        <template #suffix>
          <SaveCancelControls @confirm="submit" @cancel="cancel" />
        </template>
      </el-input>
      <div v-else-if="type === 'dict'">
        <slot
          name="dict"
          :v-model="inputValue"
          :disabled="disabled"
          :label="label"
          :readonly="readonly"
          :type="type"
          :placeholder="placeholder"
          :is-dict="isDict"
          :update-model-value="handleDictUpdate"
          :save="submit"
          :cancel="cancel"
        />
      </div>
      <el-input
        v-else
        v-model="inputValue as unknown as string | null"
        size="small"
        class="w-full"
        :disabled="disabled"
        :readonly="readonly"
        :placeholder="label"
      >
        <template #suffix>
          <SaveCancelControls @confirm="submit" @cancel="cancel" />
        </template>
      </el-input>
    </template>
  </div>
</template>

<style scoped>
.button-new-tag {
  margin-top: 4px;
  font-size: 12px;
  padding: 2px 6px;
}
:deep(.el-input__wrapper) {
  box-shadow: none !important;
  padding: 0 !important;
  background-color: transparent !important;
}
</style>
