<script lang="ts">
  import Sidebar from "./Sidebar.svelte"
  import Calendar from "./Calendar.svelte";
  import Header from "./Header.svelte";
</script>

<div class="h-[20px]">
  <Header/>
  <div class="grid grid-cols-[auto_1fr]">
	  <div>
		  <Sidebar />
	  </div>
	  <div id="main">
  		<Calendar />
	  </div>
  </div>
</div>