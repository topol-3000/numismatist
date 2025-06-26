import "./assets/css/satoshi.css";
import "./assets/css/style.css";
import "flatpickr/dist/flatpickr.min.css";
import "@vue-js-cron/light/dist/light.css";

import CronLightPlugin from "@vue-js-cron/light";
import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";
import router from "./router";

const app = createApp(App);

app.use(CronLightPlugin);
app.use(createPinia());
app.use(router);

app.mount("#app");
