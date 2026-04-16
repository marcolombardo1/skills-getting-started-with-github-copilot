document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  function escapeHtml(value) {
    return value
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  function createParticipantsMarkup(participants) {
    if (!participants.length) {
      return '<li class="participants-empty">No students signed up yet</li>';
    }

    return participants
      .map(
        (participant) => `
          <li class="participant-row">
            <span class="participant-email">${escapeHtml(participant)}</span>
            <button
              type="button"
              class="participant-remove-button"
              data-email="${escapeHtml(participant)}"
              aria-label="Remove ${escapeHtml(participant)}"
              title="Remove participant"
            >
              <span class="participant-remove-icon" aria-hidden="true">&times;</span>
            </button>
          </li>
        `
      )
      .join("");
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const safeActivityName = escapeHtml(name);

        activityCard.innerHTML = `
          <h4>${safeActivityName}</h4>
          <p class="activity-description">${escapeHtml(details.description)}</p>
          <div class="activity-meta">
            <p><strong>Schedule:</strong> ${escapeHtml(details.schedule)}</p>
            <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          </div>
          <div class="participants-section" data-activity="${safeActivityName}">
            <p class="participants-title">Current participants</p>
            <ul class="participants-list">
              ${createParticipantsMarkup(details.participants)}
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  activitiesList.addEventListener("click", async (event) => {
    const removeButton = event.target.closest(".participant-remove-button");

    if (!removeButton) {
      return;
    }

    const participantsSection = removeButton.closest(".participants-section");
    const activityName = participantsSection?.dataset.activity;
    const participantEmail = removeButton.dataset.email;

    if (!activityName || !participantEmail) {
      showMessage("Unable to remove this participant.", "error");
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/participants?email=${encodeURIComponent(participantEmail)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        fetchActivities();
        return;
      }

      showMessage(result.detail || "An error occurred", "error");
    } catch (error) {
      showMessage("Failed to remove participant. Please try again.", "error");
      console.error("Error removing participant:", error);
    }
  });

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
