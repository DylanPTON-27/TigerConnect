export const themeState = $state({
  themeIsDark: false,
  toggleTheme() {
    this.themeIsDark = !this.themeIsDark;
  }
});

export let selectedFriend = $state({
  name: "",
  netid: "",
  photo: "",
  changeFriend(friend, netid, photo) {
    this.name = friend;
    this.netid = netid;
    this.photo = photo;
  }
});

export let reloadConvos = $state({
  change: false,
  toggle() {
    this.change = !this.change;
  }
});

export let usersDict = $state({
  users: [],
  setUsers(users) {
    this.users = users;
  }
});