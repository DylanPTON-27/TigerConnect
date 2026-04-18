export const sidebarState = $state({
  sidebarState: 'closed', // closed, open, add
  toggleSidebar() {
    if (this.sidebarState === 'closed') {
      this.sidebarState = 'open';
    } else {
      this.sidebarState = 'closed';
    }
  },
  toggleList() {
    if (this.sidebarState === 'open') {
      this.sidebarState = 'add';
    } else if (this.sidebarState === 'add') {
      this.sidebarState = 'open'
    }
  }
});

export const themeState = $state({
  themeIsDark: false,
  toggleTheme() {
    this.themeIsDark = !this.themeIsDark;
  }
});
