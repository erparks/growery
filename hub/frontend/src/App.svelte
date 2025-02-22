<script>
  import { Router, Route } from "svelte-routing";
  import Home from "./routes/index.svelte";
  import { onMount } from "svelte";

  let data = null;
  let error = null;

  onMount(async () => {
    try {
      const res = await fetch("http://10.0.0.181:5000/api/plants");
      if (!res.ok) throw new Error("Failed to fetch data");
      data = await res.json();
    } catch (err) {
      error = err.message;
    }
  });

  $: console.log(data);
</script>

<Router>
  <div>
    <Route path="/about" component={Home} />
  </div>
</Router>
