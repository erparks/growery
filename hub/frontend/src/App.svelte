<script>
  import { Router, Route } from "svelte-routing";
  import Home from "./routes/index.svelte";
</script>

<Router>
  <div>
    <Route path="/about" component={Home} />
  </div>
</Router>
