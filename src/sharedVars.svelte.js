export const drawerState = $state({
  showDrawers: true,
  toggleDrawers() {
    this.showDrawers = !this.showDrawers;
  }
});