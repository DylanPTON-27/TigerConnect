export const sidebarState = $state({
  sidebarOpen: false,
  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
  }
});

export const themeState = $state({
  themeIsDark: false,
  toggleTheme() {
    this.themeIsDark = !this.themeIsDark;
  }
});