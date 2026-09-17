const tabs = document.querySelectorAll(".tab");
const container = document.getElementById("matches-container");


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


function createTeam(team) {
    return `
        <div class="team">
            <img
                class="team-logo"
                src="${team.logo_url}"
                alt="${team.name}"
            >

            <span class="team-name">
                ${team.name}
            </span>
        </div>
    `;
}


function createMatchCard(match) {
    const status = getMatchStatus(match);

    return `
        <article
            class="match-card"
            data-match-id="${match.id}"
        >
            <div class="match-competition">
                <div class="competition-info">
                    ${
                        match.competition.logo_url
                            ? `
                                <img
                                    class="competition-logo"
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
            </div>

            <div class="match-teams">
                ${createTeam(match.home_team)}

                <div class="match-score">
                    <strong>
                        ${match.home_score} - ${match.away_score}
                    </strong>

                    <span
                        class="match-status ${
                            status === "LIVE" ? "live" : ""
                        }"
                    >
                        ${status}
                    </span>
                </div>

                ${createTeam(match.away_team)}
            </div>
        </article>
    `;
}


function showMessage(message) {
    container.innerHTML = `
        <div class="loading">
            ${message}
        </div>
    `;
}


async function loadMatches(filter = "today") {
    showMessage("Loading matches...");

    try {
        let url = "/api/v1/matches/";

        if (filter === "live") {
            url += "?status=LIVE";
        }

        if (filter === "finished") {
            url += "?status=FT";
        }

        if (filter === "upcoming") {
            url += "?status=NS";
        }

        if (filter === "today") {
            const today = new Date()
                .toISOString()
                .split("T")[0];

            url += `?date=${today}`;
        }

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(
                "Failed to load matches"
            );
        }

        const data = await response.json();

        if (data.matches.length === 0) {
            showMessage("No matches found.");
            return;
        }

        container.innerHTML = data.matches
            .map(createMatchCard)
            .join("");

        addMatchCardListeners();

    } catch (error) {
        console.error(error);

        showMessage(
            "Unable to load matches."
        );
    }
}


function addMatchCardListeners() {
    const cards = document.querySelectorAll(
        ".match-card"
    );

    cards.forEach((card) => {
        card.addEventListener(
            "click",
            () => {
                const matchId = card.dataset.matchId;

                window.location.href =
                    `/matches/${matchId}`;
            },
        );
    });
}


tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        tabs.forEach((item) => {
            item.classList.remove("active");
        });

        tab.classList.add("active");

        const filter = tab.textContent
            .trim()
            .toLowerCase();

        loadMatches(filter);
    });
});


document.addEventListener(
    "DOMContentLoaded",
    () => {
        loadMatches("today");
    },
);