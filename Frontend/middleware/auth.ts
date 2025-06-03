export default defineNuxtRouteMiddleware((to, from) => {
  const { isLoggedIn, user } = useAuthStore();
  if (!isLoggedIn.value && !to.path.startsWith("/auth")) {
    return navigateTo("/auth/login");
  }
  const role = user.value?.role;
  if (to.path.startsWith("/admin") && role !== "admin") {
    return navigateTo("/");
  }

  if (to.path.startsWith("/teacher") && role !== "teacher") {
    return navigateTo("/");
  }

  if (to.path.startsWith("/student") && role !== "student") {
    return navigateTo("/");
  }
});
