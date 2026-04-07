<script lang="ts">
  import Sidebar from "./Sidebar.svelte"
  import Main from "./Main.svelte";
  import Header from "./Header.svelte";
</script>

<div class="h-[20px]">
  <Header/>
  <div class="grid grid-cols-[auto_1fr]">
	  <div>
		  <Sidebar />
	  </div>
	  <div id="main">
  		<Main />
	  </div>
  </div>
</div>