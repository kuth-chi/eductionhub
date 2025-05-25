document.getElementById("searchInput").addEventListener("keyup", function (e) {
  const query = e.target.value.trim(); // Get search input
  const url = `/api/schools-list/?search=${encodeURIComponent(query)}`;

  // AJAX Request
  fetch(url)
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById("school-container");

      if (data.length === 0) {
        container.innerHTML = `
          <p class="text-gray-500 dark:text-gray-400">No results found</p>
        `;
        return;
      }

      // Render Schools
      container.innerHTML = data.map(school => `
        <div class="text-center text-gray-500 dark:text-gray-400 hover:bg-slate-200 dark:hover:bg-slate-700 hover:border-gray-700 dark:hover:border-gray-700 rounded-lg p-4">
          <img 
            class="mx-auto mb-4 w-36 h-36 rounded-full object-cover"
            src="${school.logo}" 
            alt="${school.name}" 
          >
          <h3 class="mb-1 text-xl font-bold tracking-tight text-gray-900 dark:text-white">
            <a href="#">${school.name}</a>
          </h3>
          <p class="text-sm">${school.educational_levels.join(", ") || "N/A"}</p>
          <p class="text-sm">${school.type.join(", ") || "N/A"}</p>
          <div class="mt-4">
            ${school.platform_profiles.map(profile => `
              <a href="${profile.profile_url}" target="_blank" class="inline-block mr-2">
                ${profile.platform.icon} ${profile.platform.name}
              </a>
            `).join("")}
          </div>
        </div>
      `).join("");
    })
    .catch(error => console.error("Error:", error));
});
