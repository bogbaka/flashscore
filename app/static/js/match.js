const container = document.getElementById(
    "match-container"
);


function getMatchStatus(match) {
    const liveStatuses = [
        "1H",
        "2H",
        "ET",
        "P",
        "LIVE",
    ];

    if (liveStatuses.includes(match.status)) {
        return "LIVE";
    }

    if (match.status === "HT") {
        return "HT";
    }

    if (match.status === "FT") {
        return "FT";
    }

    if (match.status === "NS") {
        return "Scheduled";
    }

    return match.status;
}


function formatMatchDate(dateString) {
    const date = new Date(dateString);

    return date.toLocaleString(
        undefined,
        {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        },
    );
}


function createTeam(team) {
    return `
        <div class="details-team">
            <img
                src="${team.logo_url}"
                alt="${team.name}"
                class="details-team-logo"
            >

            <h2>
                ${team.name}
            </h2>

            <span class="team-short-name">
                ${team.short_name || ""}
            </span>
        </div>
    `;
}


function getEventIcon(eventType) {
    if (eventType === "Goal") {
        return "⚽";
    }

    if (eventType === "Card") {
        return "🟨";
    }

    if (eventType === "subst") {
        return "🔄";
    }

    return "•";
}


function createEvent(event) {
    return `
        <div class="match-event">
            <span class="event-minute">
                ${event.minute ?? ""}'
            </span>

            <span class="event-icon">
                ${getEventIcon(event.event_type)}
            </span>

            <div class="event-info">
                <strong>
                    ${event.player_name || "Unknown"}
                </strong>

                <span>
                    ${event.description || event.event_type}
                </span>
            </div>
        </div>
    `;
}


function renderMatch(match) {
    const status = getMatchStatus(match);

    const events = match.events.length
        ? match.events
            .map(createEvent)
            .join("")
        : `
            <div class="loading">
                No match events recorded.
            </div>
        `;

    container.innerHTML = `
        <section class="match-details">

            <a
                href="/"
                class="back-link"
            >
                ← Back to matches
            </a>

            <div class="details-competition">

                ${
                    match.competition.logo_url
                        ? `
                            <img
                                src="${match.competition.logo_url}"
                                alt="${match.competition.name}"
                            >
                        `
                        : ""
                }

                <span>
                    ${match.competition.name}
                </span>

            </div>

            <div class="details-date">
                ${formatMatchDate(match.kickoff_at)}
            </div>

            <div class="details-score">

                ${createTeam(match.home_team)}

                <div class="details-result">

                    <strong>
                        ${match.home_score}
                        -
                        ${match.away_score}
                    </strong>

                    <span
                        class="match-status ${
                            status === "LIVE"
                                ? "live"
                                : ""
                        }"
                    >
                        ${status}
                    </span>

                </div>

                ${createTeam(match.away_team)}

            </div>

        </section>

        <section class="events-section">

            <div class="section-heading">
                <h2>Match Events</h2>
            </div>

            <div class="events-list">
                ${events}
            </div>

        </section>
    `;
}


async function loadMatch() {
    const matchId = window.location.pathname
        .split("/")
        .pop();

    try {
        const response = await fetch(
            `/api/v1/matches/${matchId}`
        );

        if (!response.ok) {
            throw new Error(
                "Failed to load match"
            );
        }

        const match = await response.json();

        renderMatch(match);

    } catch (error) {
        console.error(error);

        container.innerHTML = `
            <div class="loading">
                Unable to load match.
            </div>
        `;
    }
}


document.addEventListener(
    "DOMContentLoaded",
    loadMatch,
);