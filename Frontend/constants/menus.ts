// menus.ts - define menus for roles
export const menus = {
  admin: [
    { title: "Dashboard", icon: "HomeFilled", route: "/admin/dashboard" },
    { title: "Manage Users", icon: "User", route: "/admin/users" },
    { title: "Manage Classes", icon: "Notebook", route: "/admin/classes" },
    { title: "Notifications", icon: "Bell", route: "/admin/notifications" },
    { title: "System Events", icon: "Calendar", route: "/admin/events" },
    { title: "Settings", icon: "Setting", route: "/admin/settings" },
  ],
  teacher: [
    { title: "Dashboard", icon: "HomeFilled", route: "/teacher/dashboard" },
    { title: "My Classes", icon: "Notebook", route: "/teacher/classes" },
    { title: "Notifications", icon: "Bell", route: "/teacher/notifications" },
    { title: "Settings", icon: "Setting", route: "/teacher/settings" },
  ],
  // Add other roles...
};
