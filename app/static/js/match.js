const container = document.getElementById(
    "match-container"
);


const LIVE_STATUSES = [
    "1H",
    "HT",
    "2H",
    "ET",
    "BT",
    "P",
    "LIVE",
];


function escapeHtml(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function isLive(match) {
    return LIVE_STATUSES.includes(
        match.status
    );
}


function getMatchStatus(match) {
    if (isLive(match)) {
        return "LIVE";
    }

    if (
        match.status === "FT" ||
        match.status === "AET" ||
        match.status === "PEN"
    ) {
        return "FT";
    }

    if (
        match.status === "NS" ||
        match.status === "TBD"
    ) {
        return "Scheduled";
    }

    return escapeHtml(
        match.status || "Unknown"
    );
}


function formatMatchDate(dateString) {
    if (!dateString) {
        return "Date unavailable";
    }

    const date = new Date(dateString);

    if (Number.isNaN(date.getTime())) {
        return "Date unavailable";
    }

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
    const logo = team.logo_url
        ? `
            <img
                src="${escapeHtml(team.logo_url)}"
                alt="${escapeHtml(team.name)}"
                class="details-team-logo"
                loading="lazy"
            >
        `
        : `
            <div
                class="details-team-logo"
                aria-hidden="true"
            >
                ⚽
            </div>
        `;

    return `
        <div class="details-team">

            ${logo}

            <h2>
                ${escapeHtml(team.name)}
            </h2>

            ${
                team.short_name
                    ? `
                        <span class="team-short-name">
                            ${escapeHtml(
                                team.short_name
                            )}
                        </span>
                    `
                    : ""
            }

        </div>
    `;
}


function getEventIcon(event) {
    const type =
        String(
            event.event_type || ""
        ).toLowerCase();

    if (type === "goal") {
        return "⚽";
    }

    if (
        type === "card" &&
        String(
            event.description || ""
        ).toLowerCase().includes("red")
    ) {
        return "🟥";
    }

    if (type === "card") {
        return "🟨";
    }

    if (
        type === "subst" ||
        type === "substitution"
    ) {
        return "🔄";
    }

    return "•";
}


function createEvent(event) {
    const minute =
        event.minute !== null &&
        event.minute !== undefined
            ? `${escapeHtml(event.minute)}'`
            : "—";

    const player =
        event.player_name ||
        "Match event";

    const description =
        event.description ||
        event.event_type ||
        "Event";

    return `
        <div class="match-event">

            <span class="event-minute">
                ${minute}
            </span>

            <span
                class="event-icon"
                aria-hidden="true"
            >
                ${getEventIcon(event)}
            </span>

            <div class="event-info">

                <strong>
                    ${escapeHtml(player)}
                </strong>

                <span>
                    ${escapeHtml(description)}
                </span>

            </div>

        </div>
    `;
}


function createEvents(events) {
    if (
        !events ||
        events.length === 0
    ) {
        return `
            <div class="empty-events">

                <strong>
                    No match events recorded.
                </strong>

                <span>
                    Goals, cards and substitutions
                    will appear here when available.
                </span>

            </div>
        `;
    }

    return events
        .map(createEvent)
        .join("");
}


function renderMatch(match) {
    const status =
        getMatchStatus(match);

    const live =
        isLive(match);

    const competition =
        match.competition || {};

    const homeTeam =
        match.home_team || {};

    const awayTeam =
        match.away_team || {};

    container.innerHTML = `
        <section class="match-header">

            <a
                href="/"
                class="back-link"
            >
                ← Back to matches
            </a>


            <div class="competition-header">

                ${
                    competition.logo_url
                        ? `
                            <img
                                src="${escapeHtml(
                                    competition.logo_url
                                )}"
                                alt="${escapeHtml(
                                    competition.name
                                )}"
                                loading="lazy"
                            >
                        `
                        : ""
                }

                <span class="competition-name">
                    ${
                        escapeHtml(
                            competition.name ||
                            "Football"
                        )
                    }
                </span>

            </div>


            <div class="match-date">
                ${formatMatchDate(
                    match.kickoff_at
                )}
            </div>


            <div class="match-scoreboard">

                ${createTeam(homeTeam)}


                <div class="details-result">

                    <strong
                        class="details-score-value"
                    >
                        ${escapeHtml(
                            match.home_score
                        )}
                        -
                        ${escapeHtml(
                            match.away_score
                        )}
                    </strong>

                    <span
                        class="match-status ${
                            live ? "live" : ""
                        }"
                    >
                        ${status}
                    </span>

                </div>


                ${createTeam(awayTeam)}

            </div>

        </section>


        <section class="events-section">

            <div class="section-heading">

                <h2>
                    Match Events
                </h2>

            </div>


            <div class="events-list">

                ${createEvents(
                    match.events
                )}

            </div>

        </section>
    `;
}


function showError(message) {
    container.innerHTML = `
        <div class="match-error">

            <strong>
                Unable to load match.
            </strong>

            <p>
                ${escapeHtml(
                    message ||
                    "Please try again."
                )}
            </p>

            <a
                href="/"
                class="back-link"
            >
                ← Back to matches
            </a>

        </div>
    `;
}


function getMatchId() {
    const parts =
        window.location.pathname
            .split("/")
            .filter(Boolean);

    return parts.at(-1);
}


async function loadMatch() {
    const matchId =
        getMatchId();

    if (!matchId) {
        showError(
            "Match ID is missing."
        );

        return;
    }

    try {
        const response = await fetch(
            `/api/v1/matches/${encodeURIComponent(
                matchId
            )}`,
            {
                headers: {
                    Accept:
                        "application/json",
                },
            }
        );

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error(
                    "Match not found."
                );
            }

            throw new Error(
                `Request failed with status ${response.status}.`
            );
        }

        const match =
            await response.json();

        renderMatch(match);

    } catch (error) {
        console.error(error);

        showError(
            error.message ||
            "Please check your connection and try again."
        );
    }
}


document.addEventListener(
    "DOMContentLoaded",
    loadMatch,
);