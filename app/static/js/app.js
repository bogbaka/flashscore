async function loadMatches() {
    const container = document.getElementById("matches-container");

    try {
        const response = await fetch("/api/v1/matches");

        if (!response.ok) {
            throw new Error("Failed to load matches");
        }

        const data = await response.json();
        const matches = data.matches;

        if (matches.length === 0) {
            container.innerHTML = `
                <div class="loading">
                    No matches found.
                </div>
            `;
            return;
        }

        container.innerHTML = matches
            .map(
                (match) => `
                    <div class="match-row">
                        <span>${match.home_team.name}</span>

                        <strong>
                            ${match.home_score} - ${match.away_score}
                        </strong>

                        <span>${match.away_team.name}</span>
                    </div>
                `,
            )
            .join("");
    } catch (error) {
        console.error(error);

        container.innerHTML = `
            <div class="loading">
                Unable to load matches.
            </div>
        `;
    }
}


document.addEventListener(
    "DOMContentLoaded",
    loadMatches,
);