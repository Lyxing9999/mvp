<script setup lang="ts">
import { ref, computed, watch, nextTick } from "vue";
import BaseDictInput from "./BaseDictInput.vue";
interface TagObject {
  label: string;
  order?: number;
}
type ModelValue = string | TagObject | string[] | number;

const props = defineProps<{
  modelValue: ModelValue;
  label: string;
  disabled?: boolean;
  type?: "number" | "float" | "date" | "string" | "email" | "dict";
  placeholder?: string;
  dateDefaultVal?: Date;
  isDate?: boolean;
  isDict?: boolean;
  readonly?: boolean;
}>();

const emit = defineEmits(["update:modelValue", "save", "cancel"]);

const inputValue = ref<string | number | Record<string, string> | null>(null);
const tags = ref<string[]>([]);
const showInputField = ref(false);
const isAddingTag = ref(false); // for inline tag input
const inputRef = ref<HTMLInputElement | null>(null);

const isArray = computed(() => Array.isArray(props.modelValue));
const isDict = computed(
  () =>
    typeof props.modelValue === "dict" &&
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

watch(
  () => props.modelValue,
  (newVal) => {
    if (Array.isArray(newVal)) {
      tags.value = newVal.map((item) =>
        typeof item === "string" ? item : ((item as TagObject).label ?? "")
      );

      inputValue.value = "";
    } else if (typeof newVal === "number") {
      inputValue.value = newVal;
      tags.value = [];
    } else if (typeof newVal === "string") {
      inputValue.value = newVal;
      tags.value = [];
    } else if (isTag.value) {
      inputValue.value = (props.modelValue as TagObject).label ?? "";
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
  if (val && !tags.value.includes(val)) {
    tags.value.push(val);
    inputValue.value = "";
  }
  isAddingTag.value = false;
}

function removeTag(index: number) {
  tags.value.splice(index, 1);
}

function submit() {
  if (isArray.value) {
    emit("update:modelValue", tags.value);
    emit("save", tags.value);
  } else if (isTag.value) {
    emit("update:modelValue", {
      ...(props.modelValue as TagObject),
      label: inputValue.value,
    });
    emit("save", {
      ...(props.modelValue as TagObject),
      label: inputValue.value,
    });
  } else {
    emit("update:modelValue", inputValue.value);
    emit("save", inputValue.value);
  }
  showInputField.value = false;
}

function cancel() {
  inputValue.value =
    typeof props.modelValue === "string"
      ? props.modelValue
      : ((props.modelValue as TagObject)?.label ?? "");
  emit("cancel");
  showInputField.value = false;
  isAddingTag.value = false;
}
function updateValue(val: Record<string, string>) {
  inputValue.value = JSON.parse(JSON.stringify(val));
  emit("update:modelValue", inputValue.value);
  emit("save", val);
}
</script>

<template>
  <div>
    <!-- ARRAY HANDLING -->
    <template v-if="isArray">
      <div v-if="showInputField" class="flex flex-wrap gap-2 items-center">
        <el-tag
          v-for="(tag, i) in tags"
          :key="i"
          closable
          @close="removeTag(i)"
          size="small"
        >
          {{ tag }}
        </el-tag>

        <!-- Tag-style input -->
        <el-tag v-if="isAddingTag" class="px-0">
          <el-input
            ref="inputRef"
            v-model="inputValue"
            class="w-20"
            size="small"
            @keyup.enter="addTag"
            @blur="addTag"
            style="border: none; outline: none"
          />
        </el-tag>

        <!-- Add tag button as tag -->
        <el-tag
          v-else
          type="info"
          class="cursor-pointer"
          @click="
            () => {
              isAddingTag = true;
              inputValue = '';
              nextTick(() => inputRef?.focus());
            }
          "
        >
          + {{ label }}
        </el-tag>

        <!-- Action buttons -->
        <div class="mt-2 w-full flex justify-end gap-2">
          <el-button size="small" @click="cancel">Cancel</el-button>
          <el-button type="primary" size="small" @click="submit"
            >Save</el-button
          >
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
        >
          {{ tag }}
        </el-tag>
        <el-tag type="info" class="cursor-pointer">+ New Tag</el-tag>
      </div>
    </template>

    <template v-else>
      <div
        v-if="!showInputField"
        class="cursor-pointer flex justify-between items-center"
        @click="showInput"
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
        size="small"
        class="w-full"
        :placeholder="label"
      >
        <template #suffix>
          <div class="flex items-center space-x-1">
            <el-popconfirm
              title="Are you sure you want to save the changes?"
              confirm-button-text="Yes"
              cancel-button-text="No"
              @confirm="submit"
            >
              <template #reference>
                <el-button
                  class="compact-btn"
                  type="text"
                  size="small"
                  icon="Edit"
                  title="Save"
                />
              </template>
            </el-popconfirm>

            <el-button
              class="compact-btn"
              type="text"
              size="small"
              icon="Close"
              @click="cancel"
              title="Cancel"
            />
          </div> </template
      ></el-input-number>
      <div
        v-else-if="type === 'date'"
        class="flex items-center space-x-2 w-full"
      >
        <el-date-picker
          v-model="inputValue as unknown as Date | null"
          :disabled="disabled"
          size="small"
          class="w-full"
          :placeholder="label"
          :default-value="props.dateDefaultVal"
        />
        <div v-if="!disabled" class="flex items-center space-x-1">
          <el-popconfirm
            title="Are you sure you want to save the changes?"
            confirm-button-text="Yes"
            cancel-button-text="No"
            @confirm="submit"
          >
            <template #reference>
              <el-button
                class="compact-btn"
                type="text"
                size="small"
                icon="Edit"
                title="Save"
              />
            </template>
          </el-popconfirm>

          <el-button
            class="compact-btn"
            type="text"
            size="small"
            icon="Close"
            @click="cancel"
            title="Cancel"
          />
        </div>
      </div>

      <el-input
        v-else-if="type === 'email'"
        v-model="inputValue as unknown as string | null"
        type="email"
        size="small"
        class="w-full"
        :placeholder="label"
      >
        <template #suffix>
          <div class="flex items-center space-x-1">
            <el-popconfirm
              title="Are you sure you want to save the changes?"
              confirm-button-text="Yes"
              cancel-button-text="No"
              @confirm="submit"
            >
              <template #reference>
                <el-button
                  class="compact-btn"
                  type="text"
                  size="small"
                  icon="Edit"
                  title="Save"
                />
              </template>
            </el-popconfirm>

            <el-button
              class="compact-btn"
              type="text"
              size="small"
              icon="Close"
              @click="cancel"
              title="Cancel"
            />
          </div>
        </template>
      </el-input>

      <div v-else-if="type === 'dict' && isDict">
        <BaseDictInput
          :readonly="true"
          :disabled="true"
          :modelValue="inputValue as unknown as Record<string, string>"
          :label="'Can not edit this field'"
          placeholder="Can not edit this field"
          @update:modelValue="updateValue"
        />
      </div>

      <el-input
        v-else
        v-model="inputValue as unknown as string | null"
        size="small"
        class="w-full"
        :disabled="disabled"
        :placeholder="label"
      >
        <template #suffix>
          <div class="flex items-center space-x-1">
            <el-popconfirm
              title="Are you sure you want to save the changes?"
              confirm-button-text="Yes"
              cancel-button-text="No"
              @confirm="submit"
            >
              <template #reference>
                <el-button
                  class="compact-btn"
                  type="text"
                  size="small"
                  icon="Edit"
                  title="Save"
                />
              </template>
            </el-popconfirm>

            <el-button
              class="compact-btn"
              type="text"
              size="small"
              icon="Close"
              @click="cancel"
              title="Cancel"
            />
          </div>
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
