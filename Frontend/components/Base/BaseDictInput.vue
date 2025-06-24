<script setup lang="ts">
import { ref, watch, computed, defineEmits, defineProps } from "vue";

const props = defineProps<{
  modelValue: Record<string, string>;
  disabled?: boolean;
}>();
const emit = defineEmits(["update:modelValue"]);

const keys = ref<string[]>([]);

watch(
  () => props.modelValue,
  (newVal) => {
    keys.value = Object.keys(newVal);
  },
  { immediate: true }
);

const rows = computed(() =>
  keys.value.map((key) => ({
    key,
    value: props.modelValue[key],
  }))
);

function updateKey(index: number, newKey: string) {
  const oldKey = keys.value[index];
  if (newKey && newKey !== oldKey && !keys.value.includes(newKey)) {
    const newObj = { ...props.modelValue };
    newObj[newKey] = newObj[oldKey];
    delete newObj[oldKey];
    keys.value[index] = newKey;
    emit("update:modelValue", newObj);
  }
}

function updateValue(key: string, value: string) {
  const newObj = { ...props.modelValue, [key]: value };
  emit("update:modelValue", newObj);
}

function addKeyValuePair() {
  let newKey = `key${keys.value.length + 1}`;
  while (keys.value.includes(newKey)) {
    newKey = `key${keys.value.length + 1}_${Math.floor(Math.random() * 1000)}`;
  }
  const newObj = { ...props.modelValue, [newKey]: "" };
  keys.value.push(newKey);
  emit("update:modelValue", newObj);
}

function removeKey(key: string) {
  const newObj = { ...props.modelValue };
  delete newObj[key];
  keys.value = Object.keys(newObj);
  emit("update:modelValue", newObj);
}
</script>

<template>
  <el-table :data="rows" style="width: 100%">
    <el-table-column label="Key" prop="key">
      <template #default="{ row, $index }">
        <el-input
          :model-value="row.key"
          :disabled="props.disabled"
          @input="(val) => updateKey($index, val)"
        />
      </template>
    </el-table-column>
    <el-table-column label="Value" prop="value">
      <template #default="{ row }">
        <el-input
          :model-value="row.value"
          :disabled="props.disabled"
          @input="(val) => updateValue(row.key, val)"
        />
      </template>
    </el-table-column>
    <el-table-column label="Actions">
      <template #default="{ row }">
        <el-button
          type="danger"
          @click="removeKey(row.key)"
          :disabled="props.disabled"
        >
          Remove
        </el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-button
    type="primary"
    @click="addKeyValuePair"
    :disabled="props.disabled"
    class="mt-2"
  >
    Add Key-Value
  </el-button>
</template>
