export const themeState = $state({
  themeIsDark: false,
  toggleTheme() {
    this.themeIsDark = !this.themeIsDark;
  }
});
