import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import SigninView from "@/views/Authentication/SigninView.vue";
import SignupView from "@/views/Authentication/SignupView.vue";
import ECommerceView from "@/views/Dashboard/ECommerceView.vue";
import FormElementsView from "@/views/Forms/FormElementsView.vue";
import FormLayoutView from "@/views/Forms/FormLayoutView.vue";
import SettingsView from "@/views/Pages/SettingsView.vue";
import ProfileView from "@/views/ProfileView.vue";
import EditScenarioView from "@/views/Scenarios/EditScenarioView.vue";
import NewScenarioView from "@/views/Scenarios/NewScenarioView.vue";
import ScenariosView from "@/views/Scenarios/ScenariosView.vue";
import TablesView from "@/views/TablesView.vue";
import AlertsView from "@/views/UiElements/AlertsView.vue";
import ButtonsView from "@/views/UiElements/ButtonsView.vue";
import EditUnitView from "@/views/Units/EditUnitView.vue";
import NewUnitView from "@/views/Units/NewUnitView.vue";
import UnitsView from "@/views/Units/UnitsView.vue";

const routes = [
  {
    path: "/",
    name: "Dashboard",
    component: ECommerceView,
    meta: {
      title: "Dashboard",
      requiresAuth: true,
    },
  },
  {
    path: "/units",
    name: "Units",
    component: UnitsView,
    meta: {
      title: "Units",
      requiresAuth: true,
    },
  },
  {
    path: "/units/:id",
    name: "Unit",
    component: EditUnitView,
    meta: {
      title: "Unit",
      requiresAuth: true,
    },
    props: true,
  },
  {
    path: "/units/new/:unit_type?",
    name: "NewUnit",
    component: NewUnitView,
    meta: {
      title: "New Unit",
      requiresAuth: true,
    },
    props: true,
  },
  {
    path: "/scenarios",
    name: "Scenarios",
    component: ScenariosView,
    meta: {
      title: "Scenarios",
      requiresAuth: true,
    },
  },
  {
    path: "/scenarios/:id",
    name: "Scenario",
    component: EditScenarioView,
    meta: {
      title: "Scenario",
      requiresAuth: true,
    },
    props: true,
  },
  {
    path: "/scenarios/new",
    name: "NewScenario",
    component: NewScenarioView,
    meta: {
      title: "New Scenario",
      requiresAuth: true,
    },
    props: true,
  },
  {
    path: "/profile",
    name: "profile",
    component: ProfileView,
    meta: {
      title: "Profile",
    },
  },
  {
    path: "/forms/form-elements",
    name: "formElements",
    component: FormElementsView,
    meta: {
      title: "Form Elements",
    },
  },
  {
    path: "/forms/form-layout",
    name: "formLayout",
    component: FormLayoutView,
    meta: {
      title: "Form Layout",
    },
  },
  {
    path: "/tables",
    name: "tables",
    component: TablesView,
    meta: {
      title: "Tables",
    },
  },
  {
    path: "/pages/settings",
    name: "settings",
    component: SettingsView,
    meta: {
      title: "Settings",
    },
  },
  {
    path: "/ui-elements/alerts",
    name: "alerts",
    component: AlertsView,
    meta: {
      title: "Alerts",
    },
  },
  {
    path: "/ui-elements/buttons",
    name: "buttons",
    component: ButtonsView,
    meta: {
      title: "Buttons",
    },
  },
  {
    path: "/auth/signin",
    name: "Login",
    component: SigninView,
    meta: {
      title: "Signin",
      requiresUnauth: true,
    },
  },
  {
    path: "/auth/signup",
    name: "signup",
    component: SignupView,
    meta: {
      title: "Signup",
    },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { left: 0, top: 0 };
  },
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: "Login" });
  } else if (to.meta.requiresUnauth && authStore.isAuthenticated) {
    next({ name: "Dashboard" });
  } else {
    document.title = `${to.meta.title}`;
    next();
  }
});

export default router;
