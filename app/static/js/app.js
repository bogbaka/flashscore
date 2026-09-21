const tabs = document.querySelectorAll(".tab");
const container = document.getElementById("matches-container");
const sectionLabel = document.getElementById("section-label");
const sectionTitle = document.getElementById("section-title");
const refreshButton = document.getElementById("refresh-button");

let currentFeed = "today";
let selectedDate = new Date();

const FEED_META = {
    live: {
        label: "LIVE NOW",
        title: "Live Matches",
    },
    today: {
        label: "TODAY",
        title: "Today's Matches",
    },
    upcoming: {
        label: "NEXT MATCHES",
        title: "Upcoming Matches",
    },
    finished: {
        label: "RECENT RESULTS",
        title: "Finished Matches",
    },
};

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
    if (value === null || value === undefined) {
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
    return LIVE_STATUSES.includes(match.status);
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

    return escapeHtml(match.status);
}

function formatKickoff(match) {
    if (!match.kickoff_at) {
        return "";
    }

    const date = new Date(match.kickoff_at);

    if (Number.isNaN(date.getTime())) {
        return "";
    }

    return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
    });
}

function createTeam(team, side) {
    const logo = team.logo_url
        ? `
            <img
                class="team-logo"
                src="${escapeHtml(team.logo_url)}"
                alt="${escapeHtml(team.name)}"
                loading="lazy"
            >
        `
        : `
            <div class="team-logo"></div>
        `;

    const content = `
        <div class="team-name">
            ${escapeHtml(team.name)}

            ${
                team.short_name
                    ? `
                        <span class="team-short-name">
                            ${escapeHtml(team.short_name)}
                        </span>
                    `
                    : ""
            }
        </div>
    `;

    if (side === "away") {
        return `
            <div class="team away">
                ${content}
                ${logo}
            </div>
        `;
    }

    return `
        <div class="team">
            ${logo}
            ${content}
        </div>
    `;
}

function createMatchCard(match) {
    const live = isLive(match);
    const status = getMatchStatus(match);
    const kickoff = formatKickoff(match);

    return `
        <article
            class="match-card"
            data-match-id="${escapeHtml(match.id)}"
        >

            <div class="match-competition">

                <div class="competition-info">

                    ${
                        match.competition &&
                        match.competition.logo_url
                            ? `
                                <img
                                    class="competition-logo"
                                    src="${escapeHtml(
                                        match.competition.logo_url
                                    )}"
                                    alt="${escapeHtml(
                                        match.competition.name
                                    )}"
                                    loading="lazy"
                                >
                            `
                            : ""
                    }

                    <span class="competition-name">
                        ${
                            match.competition
                                ? escapeHtml(
                                    match.competition.name
                                )
                                : "Football"
                        }
                    </span>

                </div>

                ${
                    kickoff
                        ? `
                            <span class="match-time">
                                ${kickoff}
                            </span>
                        `
                        : ""
                }

            </div>

            <div class="match-teams">

                ${createTeam(
                    match.home_team,
                    "home"
                )}

                <div class="match-score">

                    <strong>
                        ${escapeHtml(match.home_score)}
                        -
                        ${escapeHtml(match.away_score)}
                    </strong>

                    <span
                        class="match-status ${
                            live ? "live" : ""
                        }"
                    >
                        ${status}
                    </span>

                    ${
                        live && match.status !== "HT"
                            ? `
                                <span class="live-minute">
                                    LIVE
                                </span>
                            `
                            : ""
                    }

                </div>

                ${createTeam(
                    match.away_team,
                    "away"
                )}

            </div>

        </article>
    `;
}

function showLoading() {
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <span>Loading matches...</span>
        </div>
    `;
}

function showEmpty(feed) {
    const messages = {
        live: [
            "No live matches right now.",
            "Live matches will appear here when games are in progress.",
        ],
        today: [
            "No matches on this date.",
            "There are no matches recorded for the selected date.",
        ],
        upcoming: [
            "No upcoming matches.",
            "Upcoming fixtures will appear here.",
        ],
        finished: [
            "No finished matches.",
            "Completed matches will appear here.",
        ],
    };

    const [title, description] =
        messages[feed] || messages.today;

    container.innerHTML = `
        <div class="empty-state">
            <strong>${title}</strong>
            <p>${description}</p>
        </div>
    `;
}

function showError() {
    container.innerHTML = `
        <div class="error-state">
            <strong>Unable to load matches.</strong>
            <p>
                Please check your connection
                and try refreshing the page.
            </p>
        </div>
    `;
}

function updateSection(feed) {
    const meta =
        FEED_META[feed] ||
        FEED_META.today;

    sectionLabel.textContent = meta.label;
    sectionTitle.textContent = meta.title;
}

function formatDateForAPI(date) {
    const year = date.getFullYear();

    const month = String(
        date.getMonth() + 1
    ).padStart(2, "0");

    const day = String(
        date.getDate()
    ).padStart(2, "0");

    return `${year}-${month}-${day}`;
}

function isToday(date) {
    const today = new Date();

    return (
        date.getFullYear() === today.getFullYear() &&
        date.getMonth() === today.getMonth() &&
        date.getDate() === today.getDate()
    );
}

function formatSelectedDate() {
    if (isToday(selectedDate)) {
        return "TODAY";
    }

    return selectedDate
        .toLocaleDateString([], {
            weekday: "short",
            day: "numeric",
            month: "short",
        })
        .toUpperCase();
}

function updateDateNavigation() {
    const dateNavigation =
        document.getElementById("date-navigation");

    if (!dateNavigation) {
        return;
    }

    const dateLabel =
        document.getElementById("selected-date");

    if (dateLabel) {
        dateLabel.textContent =
            formatSelectedDate();
    }
}

function changeDate(days) {
    selectedDate = new Date(selectedDate);

    selectedDate.setDate(
        selectedDate.getDate() + days
    );

    updateDateNavigation();
    loadFeed(currentFeed);
}

async function loadFeed(feed = "today") {
    currentFeed = feed;

    updateSection(feed);
    updateDateNavigation();
    showLoading();

    try {
        const date =
            formatDateForAPI(selectedDate);

        const response = await fetch(
            `/api/v1/feed/?feed_date=${date}&limit=20`,
            {
                headers: {
                    Accept: "application/json",
                },
            }
        );

        if (!response.ok) {
            throw new Error(
                `Feed request failed: ${response.status}`
            );
        }

        const data =
            await response.json();

        const matches =
            data[feed] || [];

        if (matches.length === 0) {
            showEmpty(feed);
            return;
        }

        container.innerHTML =
            matches
                .map(createMatchCard)
                .join("");

        addMatchCardListeners();

    } catch (error) {
        console.error(error);
        showError();
    }
}

function addMatchCardListeners() {
    const cards =
        document.querySelectorAll(".match-card");

    cards.forEach((card) => {
        card.addEventListener(
            "click",
            () => {
                const matchId =
                    card.dataset.matchId;

                window.location.href =
                    `/matches/${matchId}`;
            }
        );
    });
}

tabs.forEach((tab) => {
    tab.addEventListener(
        "click",
        () => {
            tabs.forEach((item) => {
                item.classList.remove("active");
            });

            tab.classList.add("active");

            loadFeed(
                tab.dataset.feed
            );
        }
    );
});

const previousDateButton =
    document.getElementById("previous-date");

const nextDateButton =
    document.getElementById("next-date");

if (previousDateButton) {
    previousDateButton.addEventListener(
        "click",
        () => {
            changeDate(-1);
        }
    );
}

if (nextDateButton) {
    nextDateButton.addEventListener(
        "click",
        () => {
            changeDate(1);
        }
    );
}

refreshButton.addEventListener(
    "click",
    () => {
        loadFeed(currentFeed);
    }
);

document.addEventListener(
    "DOMContentLoaded",
    () => {
        updateDateNavigation();
        loadFeed("today");
    }
);