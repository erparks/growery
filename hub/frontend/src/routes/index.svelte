<script>
    import { useLocation } from "svelte-routing";
    let data = {}; // Initialize state

    async function fetchData() {
        try {
            console.log("Fetching data...");
            const response = await fetch("/api/data");
            data = await response.json();
            console.log("Fetched:", data);
        } catch (error) {
            console.error("Error fetching data:", error);
        }
    }

    const location = useLocation(); // Get current location

    console.log("Router is mounting, location:", window.location.pathname);

    $: console.log("Current location:", location);
    $: fetchData();
</script>

<div>
    <h1>growery {data?.message || "Loading..."}</h1>
</div>
