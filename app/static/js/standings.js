const container = document.getElementById(
    "standings-container"
);


function showMessage(message) {
    container.innerHTML = `
        <div class="loading">
            ${message}
        </div>
    `;
}


function createTeamCell(standing) {
    const team = standing.team;

    return `
        <div class="standing-team">
            ${
                team.logo_url
                    ? `
                        <img
                            src="${team.logo_url}"
                            alt="${team.name}"
                            class="standing-team-logo"
                        >
                    `
                    : ""
            }

            <span>
                ${team.name}
            </span>
        </div>
    `;
}


function createStandingRow(standing) {
    return `
        <tr>
            <td class="position">
                ${standing.position}
            </td>

            <td>
                ${createTeamCell(standing)}
            </td>

            <td>
                ${standing.played}
            </td>

            <td>
                ${standing.wins}
            </td>

            <td>
                ${standing.draws}
            </td>

            <td>
                ${standing.losses}
            </td>

            <td>
                ${standing.goals_for}
            </td>

            <td>
                ${standing.goals_against}
            </td>

            <td class="points">
                ${standing.points}
            </td>
        </tr>
    `;
}


function renderStandings(standings) {
    container.innerHTML = `
        <div class="standings-table-wrapper">
            <table class="standings-table">
                <thead>
                    <tr>
                        <th>Pos</th>
                        <th>Team</th>
                        <th>P</th>
                        <th>W</th>
                        <th>D</th>
                        <th>L</th>
                        <th>GF</th>
                        <th>GA</th>
                        <th>Pts</th>
                    </tr>
                </thead>

                <tbody>
                    ${standings
                        .map(createStandingRow)
                        .join("")}
                </tbody>
            </table>
        </div>
    `;
}


async function loadStandings() {
    showMessage("Loading standings...");

    try {
        const response = await fetch(
            "/api/v1/standings/"
        );

        if (!response.ok) {
            throw new Error(
                "Failed to load standings"
            );
        }

        const standings = await response.json();

        if (standings.length === 0) {
            showMessage(
                "No standings available."
            );

            return;
        }

        renderStandings(standings);

    } catch (error) {
        console.error(error);

        showMessage(
            "Unable to load standings."
        );
    }
}


document.addEventListener(
    "DOMContentLoaded",
    loadStandings,
);