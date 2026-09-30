async function apiRequest(
    url,
    options = {}
) {

    const response = await fetch(
        url,
        {
            credentials: "include",
            ...options
        }
    );


    const data =
        await response.json()
            .catch(
                () => ({
                    detail:
                        "Server returned an invalid response."
                })
            );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Something went wrong."
        );

    }


    return data;
}


/* Prevent HTML injection */

function escapeHtml(value) {

    return String(
        value ?? ""
    )
    .replace(
        /[&<>"']/g,
        character => {

            const entities = {

                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"

            };

            return entities[
                character
            ];

        }
    );

}


/* Render AI results */

function renderResults(
    data,
    container
) {

    let html = `

        <div class="result">

            <h2>
                ${escapeHtml(
                    data.summary ||
                    "Your Recommendation Plan"
                )}
            </h2>

    `;


    if (
        data.budget_allocation &&
        data.budget_allocation.length
    ) {

        html += `
            <h3>
                Budget Allocation
            </h3>

            <div class="allocation">
        `;


        data.budget_allocation.forEach(
            item => {

                html += `

                    <span class="pill">

                        ${escapeHtml(
                            item.category
                        )}

                        :

                        ₹${Number(
                            item.amount || 0
                        ).toLocaleString("en-IN")}

                        (${escapeHtml(
                            item.percentage || 0
                        )}%)

                    </span>

                `;

            }
        );


        html += `
            </div>
        `;

    }


    html += `
        <h3>
            Recommendations
        </h3>
    `;


    const recommendations =
        data.recommendations || [];


    if (!recommendations.length) {

        html += `
            <p class="small">
                No recommendations were returned.
            </p>
        `;

    }


    recommendations.forEach(
        recommendation => {

            html += `

                <div class="recommendation">

                    <h4>
                        ${escapeHtml(
                            recommendation.name
                        )}
                    </h4>

                    <div class="small">

                        ${escapeHtml(
                            recommendation.category ||
                            ""
                        )}

                        •

                        ${escapeHtml(
                            recommendation.platform ||
                            ""
                        )}

                    </div>


                    <div class="price">

                        ₹${Number(
                            recommendation.estimated_price ||
                            0
                        ).toLocaleString("en-IN")}

                    </div>


                    <p>

                        ${escapeHtml(
                            recommendation.reason ||
                            ""
                        )}

                    </p>

            `;


            if (
                recommendation.link
            ) {

                html += `

                    <a

                        href="${escapeHtml(
                            recommendation.link
                        )}"

                        target="_blank"

                        rel="noopener noreferrer"

                        class="btn"

                    >

                        Search on
                        ${escapeHtml(
                            recommendation.platform ||
                            "Platform"
                        )}

                    </a>

                `;

            }


            html += `
                </div>
            `;

        }
    );


    if (
        data.tips &&
        data.tips.length
    ) {

        html += `
            <h3>
                Smart Tips
            </h3>

            <ul>
        `;


        data.tips.forEach(
            tip => {

                html += `
                    <li>
                        ${escapeHtml(tip)}
                    </li>
                `;

            }
        );


        html += `
            </ul>
        `;

    }


    if (data.warning) {

        html += `

            <p class="small">

                ${escapeHtml(
                    data.warning
                )}

            </p>

        `;

    }


    html += `
        </div>
    `;


    container.innerHTML = html;
}


/* Login */

function setupLogin() {

    const form =
        document.getElementById(
            "loginForm"
        );


    if (!form) {

        return;
    }


    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();


            const message =
                document.getElementById(
                    "message"
                );


            message.textContent =
                "Logging in...";


            const formData =
                new FormData(form);


            const payload = {

                email:
                    formData.get("email"),

                password:
                    formData.get("password")

            };


            try {

                await apiRequest(
                    "/api/login",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );


                window.location.href =
                    "/dashboard";


            } catch (error) {

                message.textContent =
                    error.message;

            }

        }
    );

}


/* Register */

function setupRegister() {

    const form =
        document.getElementById(
            "registerForm"
        );


    if (!form) {

        return;
    }


    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();


            const message =
                document.getElementById(
                    "message"
                );


            message.textContent =
                "Creating account...";


            const formData =
                new FormData(form);


            const payload = {

                name:
                    formData.get("name"),

                email:
                    formData.get("email"),

                password:
                    formData.get("password")

            };


            try {

                await apiRequest(
                    "/api/register",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );


                window.location.href =
                    "/dashboard";


            } catch (error) {

                message.textContent =
                    error.message;

            }

        }
    );

}


/* Home Planner */

function setupHomePlanner() {

    const form =
        document.getElementById(
            "homeForm"
        );


    if (!form) {

        return;
    }


    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();


            const results =
                document.getElementById(
                    "results"
                );


            results.innerHTML = `
                <div class="result">
                    Generating your plan...
                </div>
            `;


            const formData =
                new FormData(form);


            const itemsText =
                String(
                    formData.get("items") || ""
                );


            const items =
                itemsText
                    .split(",")
                    .map(
                        item => item.trim()
                    )
                    .filter(Boolean)
                    .map(
                        item => ({
                            item,
                            quantity: 1
                        })
                    );


            const payload = {

                budget:
                    Number(
                        formData.get("budget")
                    ),

                room_type:
                    formData.get(
                        "room_type"
                    ),

                style:
                    formData.get(
                        "style"
                    ),

                items

            };


            try {

                const data =
                    await apiRequest(
                        "/api/generate-home",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify(
                                    payload
                                )
                        }
                    );


                renderResults(
                    data,
                    results
                );


            } catch (error) {

                results.innerHTML = `

                    <div class="result">

                        ${escapeHtml(
                            error.message
                        )}

                    </div>

                `;

            }

        }
    );

}


/* Party Planner */

function setupPartyPlanner() {

    const form =
        document.getElementById(
            "partyForm"
        );


    if (!form) {

        return;
    }


    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();


            const results =
                document.getElementById(
                    "results"
                );


            results.innerHTML = `
                <div class="result">
                    Creating your party plan...
                </div>
            `;


            const formData =
                new FormData(form);


            const payload = {

                budget:
                    Number(
                        formData.get(
                            "budget"
                        )
                    ),

                guests:
                    Number(
                        formData.get(
                            "guests"
                        )
                    ),

                event_type:
                    formData.get(
                        "event_type"
                    ),

                venue:
                    formData.get(
                        "venue"
                    ),

                preferences:
                    formData.get(
                        "preferences"
                    )

            };


            try {

                const data =
                    await apiRequest(
                        "/api/generate-party",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify(
                                    payload
                                )
                        }
                    );


                renderResults(
                    data,
                    results
                );


            } catch (error) {

                results.innerHTML = `

                    <div class="result">

                        ${escapeHtml(
                            error.message
                        )}

                    </div>

                `;

            }

        }
    );

}


/* Jewelry Planner */

function setupJewelryPlanner() {

    const form =
        document.getElementById(
            "jewelryForm"
        );


    if (!form) {

        return;
    }


    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();


            const results =
                document.getElementById(
                    "results"
                );


            results.innerHTML = `
                <div class="result">
                    Analyzing your jewelry requirements...
                </div>
            `;


            const formData =
                new FormData(form);


            formData.set(
                "budget",
                formData.get("budget")
            );


            try {

                const data =
                    await apiRequest(
                        "/api/generate-jewelry",
                        {
                            method: "POST",

                            body:
                                formData
                        }
                    );


                renderResults(
                    data,
                    results
                );


            } catch (error) {

                results.innerHTML = `

                    <div class="result">

                        ${escapeHtml(
                            error.message
                        )}

                    </div>

                `;

            }

        }
    );

}


/* Dashboard */

async function setupDashboard() {

    const container =
        document.getElementById(
            "dashboardContent"
        );


    if (!container) {

        return;
    }


    try {

        const data =
            await apiRequest(
                "/api/session-data"
            );


        container.innerHTML = `

            <div class="result">

                <h1>

                    Hello,
                    ${escapeHtml(
                        data.user.name
                    )}
                    👋

                </h1>

                <p>

                    Welcome to your
                    PocketSmart AI dashboard.

                </p>

                <p>

                    You have created

                    <strong>
                        ${data.recommendation_count}
                    </strong>

                    recommendation plan(s).

                </p>

            </div>

        `;

    } catch (error) {

        window.location.href =
            "/login";

    }

}


/* History */

async function setupHistory() {

    const container =
        document.getElementById(
            "history"
        );


    if (!container) {

        return;
    }


    try {

        const history =
            await apiRequest(
                "/api/history"
            );


        if (!history.length) {

            container.innerHTML = `

                <div class="result">

                    <h3>
                        No history yet
                    </h3>

                    <p>
                        Create your first
                        recommendation plan.
                    </p>

                </div>

            `;

            return;
        }


        container.innerHTML =
            history.map(
                item => {

                    const response =
                        item.response || {};


                    return `

                        <div class="result">

                            <h3>

                                ${escapeHtml(
                                    item.planner
                                        .toUpperCase()
                                )}

                            </h3>

                            <p class="small">

                                ${escapeHtml(
                                    item.created_at
                                )}

                            </p>


                            <p>

                                ${escapeHtml(
                                    response.summary ||
                                    "Recommendation plan"
                                )}

                            </p>

                        </div>

                    `;

                }
            ).join("");


    } catch (error) {

        container.innerHTML = `

            <div class="result">

                ${escapeHtml(
                    error.message
                )}

            </div>

        `;

    }

}


/* Logout */

function setupLogout() {

    const button =
        document.getElementById(
            "logoutBtn"
        );


    if (!button) {

        return;
    }


    button.addEventListener(
        "click",
        async () => {

            try {

                await apiRequest(
                    "/api/logout",
                    {
                        method: "POST"
                    }
                );

            } finally {

                window.location.href =
                    "/";

            }

        }
    );

}


/* Start everything */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupLogin();

        setupRegister();

        setupHomePlanner();

        setupPartyPlanner();

        setupJewelryPlanner();

        setupDashboard();

        setupHistory();

        setupLogout();

    }
);