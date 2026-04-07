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
        <p> Status Page WIP. </p>
        <p> Click on Calendar at top for more fleshed out Calendar Page. </p>
        <p> Menu Icon in top left works only in Calendar view right now. </p>
        <p> TigerConnect redirects to here. </p>
        <p> Toggle Light/Dark is setup but isn't connected to the actual calendar in Calendar.svelte </p>
        <p> Notifcations view should be pretty much done. </p>
        <p> Log out just redirects to a landing page that only has a login button. Needs to be connected to CAS auth. </p>
	  </div>
  </div>
</div>