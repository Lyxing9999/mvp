<script lang="ts" setup>
const props = defineProps<{
  modelValue: boolean;
  loading: boolean;
  title: string;
  infoObject: Record<string, any> | null;
  fields: {
    label: string;
    key: string;
    isArray?: boolean;
    isDate?: boolean;
    isObject?: boolean;
    children?: any[];
  }[];
  width: string;
}>();

const emit = defineEmits<{
  (event: "update:modelValue", value: boolean): void;
}>();

function getNestedValue(obj: any, key: string) {
  console.log("getNestedValue called with obj:", obj, "and key:", key);
  if (!obj) return null;
  const keys = key.split(".");
  let result = obj;
  for (const k of keys) {
    if (result == null) {
      console.log(`Key path broken at ${k}, returning null`);
      return null;
    }
    result = result[k];
  }
  console.log(`Value for key "${key}":`, result);
  return result;
}
</script>

<template>
  <el-dialog
    :model-value="modelValue"
    :title="title"
    :width="width"
    @close="emit('update:modelValue', false)"
  >
    <el-skeleton :loading="loading" animated>
      <template v-if="infoObject">
        <el-descriptions :column="1" border>
          <el-descriptions-item
            v-for="(item, index) in fields"
            :key="index"
            :label="item.label"
          >
            <template v-if="item.children && item.children.length">
              <el-descriptions :column="1" border>
                <el-descriptions-item
                  v-for="(child, idx) in item.children"
                  :key="idx"
                  :label="child.label"
                >
                  <template v-if="$slots.custom">
                    <slot
                      name="custom"
                      :item="child"
                      :infoObject="infoObject"
                      :value="getNestedValue(infoObject, child.key)"
                      :fields="fields"
                    />
                  </template>
                  <template v-else>
                    {{ getNestedValue(infoObject, child.key) || "N/A" }}
                  </template>
                </el-descriptions-item>
              </el-descriptions>
            </template>

            <template v-else-if="$slots.custom">
              <slot
                name="custom"
                :item="item"
                :infoObject="infoObject"
                :value="getNestedValue(infoObject, item.key)"
                :fields="fields"
              />
            </template>

            <template v-else>
              {{ getNestedValue(infoObject, item.key) || "N/A" }}
            </template>
          </el-descriptions-item>
        </el-descriptions>
      </template>
    </el-skeleton>
  </el-dialog>
</template>
