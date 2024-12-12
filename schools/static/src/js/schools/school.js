document.addEventListener("DOMContentLoaded", function() {
    if (typeof PAGE_NAME !== "undefined") {
        const script = document.createElement("script");
        script.src = `${window.location.origin}/static/src/js/schools/${PAGE_NAME}.js`;
        script.async = true;
        document.body.appendChild(script);
    }
}); 

// Using 
// Block Script with the following
// <script> 
// const PAGE_NAME = "{{ page_name }}";
// </script>