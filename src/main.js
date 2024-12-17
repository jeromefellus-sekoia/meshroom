import { createApp, reactive, watch, watchEffect } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import { App, ROUTES } from "./App";
import { noNulls } from "./utils";
import "./style.scss";

export const UI = reactive({
  locationHash: Object.fromEntries(
    new URLSearchParams(location.hash.substring(1)).entries()
  ),
  queryParams: Object.fromEntries(
    new URLSearchParams(location.search.substring(1)).entries()
  ),
  toasts: [],
});

export const router = createRouter({
  history: createWebHistory(),
  routes: ROUTES,
});

// Sync query parameters with UI.queryParams object, reactively
watchEffect(() => {
  const qp = new URLSearchParams(noNulls(UI.queryParams)).toString();
  if (qp) router.push(location.pathname + "?" + qp);
  else router.push(location.pathname);
});
watch(
  router.currentRoute,
  () =>
    (UI.queryParams = Object.fromEntries(
      new URLSearchParams(location.search.substring(1)).entries()
    ))
);

const app = createApp(App);
app.use(router);
app.mount("#app");
