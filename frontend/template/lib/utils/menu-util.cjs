"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const vue = require("vue");
const vueRouter = require("vue-router");
const util = require("../ele-pro-layout/util");
const common = require("./common");
function getIframeRouteComponent(menu, name) {
  return vue.defineComponent({
    name,
    setup() {
      const proLayoutState = util.useProLayoutState();
      const route = vueRouter.useRoute();
      const { fullPath } = route;
      const iframeSrc = vue.ref(util.getIframeSrc(fullPath, menu.component));
      const isAlive = menu.meta?.keepAlive !== false;
      const keepAlive = vue.computed(() => !!proLayoutState.keepAlive);
      return () => {
        if (!isAlive || !keepAlive.value) {
          return vue.h("iframe", {
            src: iframeSrc.value,
            class: "ele-admin-iframe"
          });
        }
        return vue.h("div", { class: "ele-none", style: { display: "none" } });
      };
    }
  });
}
function camelCase(str) {
  const val = str.replace(/[-|/](\w)/g, (_, c) => c ? c.toUpperCase() : "");
  return val.charAt(0).toUpperCase() + val.slice(1);
}
function pathIsAdd(path, data) {
  return common.findTree(data, (d) => path === d.path) != null;
}
function getRoutePath(path) {
  if (!path || !path.includes("?") || path.endsWith("?")) {
    return path;
  }
  return path.substring(0, path.indexOf("?"));
}
function getRouteComponent(menu, name, func) {
  if (!menu.component || !common.isExternalLink(menu.component)) {
    return { component: func(menu.component, menu, name) };
  }
  return { component: getIframeRouteComponent(menu, name), link: true };
}
function menuToRoutes(menus, getComponent, added) {
  if (!menus?.length) {
    return;
  }
  const routes = [];
  const addedRoutes = added ? [...added] : [];
  menus.forEach((item) => {
    const meta = { ...item.meta };
    const path = meta.routePath || getRoutePath(item.path);
    if (path && !common.isExternalLink(path) && !pathIsAdd(path, addedRoutes)) {
      const name = item.name || camelCase(path);
      const { component, link } = getRouteComponent(item, name, getComponent);
      if (link) {
        meta.iframe = item.component;
        meta.hideFooter = true;
      }
      addedRoutes.push({ path });
      routes.push({
        name,
        path,
        component,
        redirect: item.redirect,
        props: item.props,
        meta,
        children: menuToRoutes(item.children, getComponent, addedRoutes)
      });
    }
  });
  return routes;
}
exports.getIframeRouteComponent = getIframeRouteComponent;
exports.menuToRoutes = menuToRoutes;
