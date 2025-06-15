import { createResolver, addComponent, addImportsSources, useNuxt, defineNuxtModule, addPluginTemplate } from '@nuxt/kit';
import * as AllComponents from 'element-plus';
import * as AllIcons from '@element-plus/icons-vue';
import { createUnplugin } from 'unplugin';
import MagicString from 'magic-string';

function resolvePath(path) {
  const { resolvePath: resolvePath2 } = createResolver(import.meta.url);
  return resolvePath2(path);
}
function getLayersDir(layers) {
  const list = [];
  for (const layer of layers) {
    const srcDir = layer.config.srcDir || layer.cwd;
    if (srcDir.includes("node_modules") && layer.config.elementPlus?.importStyle !== false) {
      list.push(srcDir);
    }
  }
  return list;
}
function isArray(value) {
  return Array.isArray(value);
}
function isVueComponent(value) {
  return typeof value === "object" && value.name && (value.props || value.emits || value.setup || value.render);
}
function toArray(value) {
  return isArray(value) ? value : [value];
}
function toRegExp(arr, flags) {
  return new RegExp(`\\b(${arr.join("|")})\\b`, flags);
}
async function genLibraryImport([name, as, from]) {
  const fromPath = await resolvePath(from);
  return `import { ${name} as ${as} } from '${fromPath}';
`;
}
async function genSideEffectsImport(from) {
  const fromPath = await resolvePath(from);
  return `import '${fromPath}';
`;
}
function genIconPresets(prefix, from) {
  return allIcons.map((name) => {
    return [name, `${prefix}${name}`, from];
  });
}
function camelize(value) {
  return value.replace(/(^|-)(\w)/g, (a, b, c) => c.toUpperCase());
}
function hyphenate(value) {
  return value.replace(/\B([A-Z])/g, "-$1").toLowerCase();
}

const libraryName = "element-plus";
const iconLibraryName = "@element-plus/icons-vue";
const optimizeDeps = ["dayjs", "dayjs/plugin/*.js", "lodash-unified"];
const allComponents = Object.entries(AllComponents).reduce((all, [key, item]) => {
  const regExp = /^El[A-Z]\w+/;
  if (isVueComponent(item) && regExp.test(key) && regExp.test(item.name ?? "")) {
    all.push(key);
  }
  return all;
}, []);
const allIcons = Object.keys(AllIcons);
const allMethods = [
  "ElLoading",
  "ElMessage",
  "ElMessageBox",
  "ElNotification"
];
const allImports = [];
const allBaseImports = [
  ["ID_INJECTION_KEY", "es/hooks/use-id/index.mjs"],
  ["ZINDEX_INJECTION_KEY", "es/hooks/use-z-index/index.mjs"],
  ["provideGlobalConfig", "es/components/config-provider/src/hooks/use-global-config.mjs"]
];
const allNoStylesComponents = [
  "ElAutoResizer",
  "ElCollection",
  "ElCollectionItem",
  "ElTooltipV2"
];
const allDirectives = {
  Loading: ["ElLoadingDirective", "ElLoading"],
  Popover: ["ElPopoverDirective", "ElPopover"],
  InfiniteScroll: "ElInfiniteScroll"
};
const allSubComponents = {
  ElAnchor: ["ElAnchorLink"],
  ElBreadcrumb: ["ElBreadcrumbItem"],
  ElButton: ["ElButtonGroup"],
  ElCarousel: ["ElCarouselItem"],
  ElCheckbox: ["ElCheckboxButton", "ElCheckboxGroup"],
  ElCollapse: ["ElCollapseItem"],
  ElCollection: ["ElCollectionItem"],
  ElContainer: ["ElAside", "ElFooter", "ElHeader", "ElMain"],
  ElDescriptions: ["ElDescriptionsItem"],
  ElDropdown: ["ElDropdownItem", "ElDropdownMenu"],
  ElForm: ["ElFormItem"],
  ElMenu: ["ElMenuItem", "ElMenuItemGroup", "ElSubMenu"],
  ElPopper: ["ElPopperArrow", "ElPopperContent", "ElPopperTrigger"],
  ElRadio: ["ElRadioGroup", "ElRadioButton"],
  ElSkeleton: ["ElSkeletonItem"],
  ElSelect: ["ElOption", "ElOptionGroup"],
  ElSplitter: ["ElSplitterPanel"],
  ElSteps: ["ElStep"],
  ElTable: ["ElTableColumn"],
  ElTableV2: ["ElAutoResizer"],
  ElTabs: ["ElTabPane"],
  ElTimeline: ["ElTimelineItem"],
  ElTour: ["ElTourStep"]
};
const defaultInjectionID = {
  prefix: 1024,
  current: 0
};
const defaultInjectionZIndex = {
  current: 0
};
const defaultInclude = [
  /\.vue$/,
  /\.vue\?vue/,
  /\.vue\?v=/,
  /\.((c|m)?j|t)sx?$/
];
const defaultExclude = [
  /[\\/]node_modules[\\/]/,
  /[\\/]\.git[\\/]/,
  /[\\/]\.nuxt[\\/]/
];
const defaults = {
  components: allComponents,
  subComponents: allSubComponents,
  directives: allDirectives,
  imports: allImports,
  baseImports: allBaseImports,
  importStyle: "css",
  themes: [],
  noStylesComponents: allNoStylesComponents,
  injectionID: defaultInjectionID,
  injectionZIndex: defaultInjectionZIndex,
  include: defaultInclude,
  exclude: defaultExclude,
  namespace: "el",
  appendTo: [],
  installMethods: [],
  icon: "ElIcon"
};

function getComponentPath(name) {
  const dir = hyphenate(name.slice(2));
  return `es/components/${dir}/index.mjs`;
}
function resolveComponents(config) {
  const { components, subComponents, icon } = config;
  const icons = icon !== false ? genIconPresets(icon, iconLibraryName) : [];
  const allComponents = /* @__PURE__ */ new Set([...components, ...icons]);
  const subComponentsMap = Object.fromEntries(
    Object.entries(subComponents).reduce((all, [key, values]) => {
      values.forEach((item) => {
        all.push([item, key]);
      });
      return all;
    }, [])
  );
  allComponents.forEach(async (item) => {
    const [name, alias, from] = toArray(item);
    const componentName = subComponentsMap[name] || name;
    const filePath = from !== iconLibraryName ? `${libraryName}/${getComponentPath(componentName)}` : from;
    addComponent({
      export: name,
      name: alias || name,
      filePath: await resolvePath(filePath)
    });
  });
}

function resolveDirectives(config, name) {
  const { directives } = config;
  if (!directives[name]) {
    return void 0;
  }
  const [directive, styleName] = toArray(directives[name]);
  const path = getComponentPath(styleName ?? directive);
  const style = styleName && getStyleDir(config, styleName);
  return [directive, `${libraryName}/${path}`, style];
}

function resolveGlobalConfig(config) {
  const { globalConfig } = config;
  return {
    filename: `${libraryName}-globalConfig.plugin.mjs`,
    getContents: () => {
      return `import { defineNuxtPlugin, provideGlobalConfig } from '#imports';

export default defineNuxtPlugin(nuxtApp => {
  provideGlobalConfig(${JSON.stringify(globalConfig)}, nuxtApp.vueApp, true);
})
`;
    }
  };
}

function _resolveImports(imports) {
  imports.forEach(async ([name, path]) => {
    addImportsSources({
      from: await resolvePath(`${libraryName}/${path}`),
      imports: toArray(name)
    });
  });
}
async function resolveImports(config) {
  const { imports, icon } = config;
  const icons = icon !== false ? genIconPresets(icon) : [];
  const allImports = new Set(imports);
  const allIcons = new Set(icons);
  _resolveImports(allImports);
  addImportsSources({
    from: await resolvePath(iconLibraryName),
    imports: [...allIcons]
  });
}
function resolveBaseImports(config) {
  const { baseImports } = config;
  const methodImports = allMethods.map((name) => {
    return [name, getComponentPath(name)];
  });
  const allBaseImports = /* @__PURE__ */ new Set([...baseImports, ...methodImports]);
  _resolveImports(allBaseImports);
}

function resolveInjection(config) {
  const { injectionID, injectionZIndex } = config;
  return {
    filename: `${libraryName}-injection.plugin.mjs`,
    getContents: () => {
      return `import { defineNuxtPlugin, ID_INJECTION_KEY, ZINDEX_INJECTION_KEY } from '#imports';

export default defineNuxtPlugin(nuxtApp => {
  nuxtApp.vueApp
    .provide(ID_INJECTION_KEY, ${JSON.stringify(injectionID)})
    .provide(ZINDEX_INJECTION_KEY, ${JSON.stringify(injectionZIndex)});
})
`;
    }
  };
}

const localePlugin = createUnplugin((options) => {
  return {
    name: `${libraryName}:locale`,
    enforce: "pre",
    transformInclude(id) {
      const regExp = new RegExp(`${libraryName}/es/hooks/use-locale/index`);
      return !!id.match(regExp);
    },
    transform(code, id) {
      const s = new MagicString(code);
      s.replace("/locale/lang/en", `/locale/lang/${options.locale}`);
      if (s.hasChanged()) {
        return {
          code: s.toString(),
          map: options.sourcemap ? s.generateMap({ source: id, includeContent: true }) : void 0
        };
      }
    }
  };
});

function resolveMethods(config) {
  const { installMethods } = config;
  return {
    filename: `${libraryName}-methods.plugin.mjs`,
    getContents: () => {
      return `import { defineNuxtPlugin, ${installMethods.join(",")} } from '#imports';

export default defineNuxtPlugin(nuxtApp => {
  ${installMethods.reduce((all, name) => `${all}.use(${name})`, "nuxtApp.vueApp")};
})
`;
    }
  };
}

function resolveOptions() {
  const nuxt = useNuxt();
  nuxt.options.build.transpile.push(libraryName);
  nuxt.options.vite.optimizeDeps ||= {};
  nuxt.options.vite.optimizeDeps.include ||= [];
  nuxt.options.vite.optimizeDeps.include.push(...optimizeDeps);
  nuxt.options.vite.optimizeDeps.exclude ||= [];
  nuxt.options.vite.optimizeDeps.exclude.push(libraryName);
}

function getStyleDir(config, name) {
  if (config.importStyle === false) {
    return void 0;
  }
  const dir = hyphenate(name.slice(2));
  const type = config.importStyle === "scss" ? "index" : "css";
  return `${libraryName}/es/components/${dir}/style/${type}.mjs`;
}
function resolveStyles(config, name) {
  const { components, noStylesComponents } = config;
  const allComponents = [...components, ...allMethods];
  if (!allComponents.includes(name) || noStylesComponents.includes(name)) {
    return void 0;
  }
  return /^El[A-Z]/.test(name) ? getStyleDir(config, name) : void 0;
}

function resolveTeleports(config) {
  const { namespace, appendTo } = config;
  const defaultId = `#${namespace}-popper-container-`;
  return {
    filename: `${libraryName}-teleports.plugin.mjs`,
    getContents: () => {
      return `import { defineNuxtPlugin } from '#imports'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.hook('app:rendered', (ctx) => {
    if (ctx.ssrContext?.teleports) {
      ctx.ssrContext.teleports = renderTeleports(ctx.ssrContext.teleports)
    }
  })
})

function renderTeleports (teleports) {
  const body = Object.entries(teleports).reduce((all, [key, value]) => {
    if (key.startsWith('${defaultId}') || ${JSON.stringify(appendTo)}.includes(key)) {
      return \`\${all}<div id="\${key.slice(1)}">\${value}</div>\`
    }
    return all
  }, teleports.body || '')
  return { ...teleports, body }
}
`;
    }
  };
}

function resolveThemes(config) {
  const nuxt = useNuxt();
  const { themes, importStyle } = config;
  const allThemes = new Set(themes);
  if (importStyle === false) {
    return;
  }
  allThemes.forEach(async (item) => {
    const isScss = importStyle === "scss";
    const theme = await resolvePath(`${libraryName}/theme-chalk${isScss ? "/src" : ""}/${item}/css-vars.${isScss ? "scss" : "css"}`);
    nuxt.options.css.push(theme);
  });
}

const componentsRegExp = /(?<=[ (])_?resolveComponent\(\s*["'](lazy-|Lazy)?([^'"]*?)["'][\s,]*[^)]*\)/g;
const directivesRegExp = /(?<=[ (])_?resolveDirective\(\s*["']([^'"]*?)["'][\s,]*[^)]*\)/g;
const methodsRegExp = toRegExp(allMethods, "g");
const transformPlugin = createUnplugin((options) => {
  const { layers, include, exclude, sourcemap, transformStyles, transformDirectives } = options;
  return {
    name: `${libraryName}:transform`,
    enforce: "post",
    transformInclude(id) {
      if (layers.some((layer) => id.startsWith(layer))) {
        return true;
      }
      if (exclude.some((pattern) => id.match(pattern))) {
        return false;
      }
      if (include.some((pattern) => id.match(pattern))) {
        return true;
      }
    },
    async transform(code, id) {
      const styles = /* @__PURE__ */ new Set();
      const directives = [];
      const s = new MagicString(code);
      let no = 0;
      const addStyles = (style) => {
        style && styles.add(style);
      };
      s.replace(componentsRegExp, (full, lazy, name) => {
        addStyles(transformStyles(camelize(name)));
        return full;
      });
      s.replace(methodsRegExp, (full, name) => {
        addStyles(transformStyles(camelize(name)));
        return full;
      });
      s.replace(directivesRegExp, (full, name) => {
        const directiveConfig = transformDirectives(camelize(name));
        if (directiveConfig) {
          const [directive, path, style] = directiveConfig;
          const aliasName = `__el_directive_${no}`;
          no += 1;
          addStyles(style);
          directives.push([directive, aliasName, path]);
          return aliasName;
        }
        return full;
      });
      if (styles.size || directives.length) {
        let imports = "";
        for (const directive of directives) {
          imports += await genLibraryImport(directive);
        }
        for (const style of styles) {
          imports += await genSideEffectsImport(style);
        }
        s.prepend(imports);
      }
      if (s.hasChanged()) {
        return {
          code: s.toString(),
          map: sourcemap ? s.generateMap({ source: id, includeContent: true }) : void 0
        };
      }
    }
  };
});

const module = defineNuxtModule({
  meta: {
    name: libraryName,
    configKey: "elementPlus",
    compatibility: {
      nuxt: ">=3"
    }
  },
  defaults,
  setup(options, nuxt) {
    const layers = getLayersDir(nuxt.options._layers);
    resolveOptions();
    resolveThemes(options);
    resolveBaseImports(options);
    nuxt.options.imports.autoImport !== false && resolveImports(options);
    nuxt.options.components !== false && resolveComponents(options);
    options.globalConfig && addPluginTemplate(resolveGlobalConfig(options));
    if (nuxt.options.ssr !== false) {
      addPluginTemplate(resolveInjection(options));
      addPluginTemplate(resolveTeleports(options));
      options.installMethods.length && addPluginTemplate(resolveMethods(options));
    }
    nuxt.hook("vite:extendConfig", (config, { isClient }) => {
      const mode = isClient ? "client" : "server";
      config.plugins = config.plugins || [];
      config.plugins.push(transformPlugin.vite({
        layers,
        include: options.include,
        exclude: options.exclude,
        sourcemap: nuxt.options.sourcemap[mode],
        transformStyles: (name) => resolveStyles(options, name),
        transformDirectives: (name) => resolveDirectives(options, name)
      }));
      if (options.defaultLocale && options.defaultLocale !== "en") {
        config.plugins.push(localePlugin.vite({
          sourcemap: nuxt.options.sourcemap[mode],
          locale: options.defaultLocale
        }));
      }
    });
    nuxt.hook("webpack:config", (configs) => {
      configs.forEach((config) => {
        const mode = config.name === "client" ? "client" : "server";
        config.plugins = config.plugins || [];
        config.plugins.push(transformPlugin.webpack({
          layers,
          include: options.include,
          exclude: options.exclude,
          sourcemap: nuxt.options.sourcemap[mode],
          transformStyles: (name) => resolveStyles(options, name),
          transformDirectives: (name) => resolveDirectives(options, name)
        }));
        if (options.defaultLocale && options.defaultLocale !== "en") {
          config.plugins.push(localePlugin.webpack({
            sourcemap: nuxt.options.sourcemap[mode],
            locale: options.defaultLocale
          }));
        }
      });
    });
  }
});

export { module as default };
