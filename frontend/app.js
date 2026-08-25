const recommendButton =
    document.getElementById(
        "recommendButton"
    );


const moviesContainer =
    document.getElementById(
        "moviesContainer"
    );


const recommendationSummary =
    document.getElementById(
        "recommendationSummary"
    );


const movieModal =
    document.getElementById(
        "movieModal"
    );


const closeModal =
    document.getElementById(
        "closeModal"
    );


const modalMovieContent =
    document.getElementById(
        "modalMovieContent"
    );


const advancedToggle =
    document.getElementById(
        "advancedToggle"
    );


const advancedPanel =
    document.getElementById(
        "advancedPanel"
    );


let currentMovies = [];



/* =====================================================
   AVANÇADO
===================================================== */

advancedToggle.addEventListener(
    "click",

    function () {


        const isHidden =
            advancedPanel.hidden;


        advancedPanel.hidden =
            !isHidden;


        advancedToggle.textContent =
            isHidden

                ? "⚙️ Ocultar opções avançadas"

                : "⚙️ Mostrar opções avançadas";

    }
);



/* =====================================================
   RECOMENDAR
===================================================== */

recommendButton.addEventListener(
    "click",

    async function () {


        const selectedGenres = [

            ...document.querySelectorAll(
                '.genres input[type="checkbox"]:checked'
            )

        ].map(
            input => input.value
        );


        const avoidGenres = [

            ...document.querySelectorAll(
                '.avoid-genres input[type="checkbox"]:checked'
            )

        ].map(
            input => input.value
        );


        const mood =
            document.getElementById(
                "mood"
            ).value;


        const rating =
            Number(

                document.getElementById(
                    "rating"
                ).value

            );


        const yearMin =
            Number(

                document.getElementById(
                    "yearMin"
                ).value

            );


        const yearMaxValue =
            document.getElementById(
                "yearMax"
            ).value;


        const runtimeValue =
            document.getElementById(
                "runtimeMax"
            ).value;


        const referenceMovie =
            document.getElementById(
                "referenceMovie"
            )
            .value
            .trim();


        const language =
            document.getElementById(
                "language"
            ).value;


        const popularityMode =
            document.getElementById(
                "popularityMode"
            ).value;


        const eraPreference =
            document.getElementById(
                "eraPreference"
            ).value;


        const resultsLimit =
            Number(

                document.getElementById(
                    "resultsLimit"
                ).value

            );


        if (
            selectedGenres.length === 0
        ) {

            alert(
                "Escolha pelo menos um gênero."
            );

            return;

        }


        if (
            !mood
        ) {

            alert(
                "Escolha o que você quer sentir."
            );

            return;

        }


        const conflictingGenres =
            selectedGenres.filter(
                genre =>
                    avoidGenres.includes(
                        genre
                    )
            );


        if (
            conflictingGenres.length
        ) {

            alert(
                "Você selecionou um gênero ao mesmo tempo para assistir e evitar."
            );

            return;

        }


        const preferences = {

            genres:
                selectedGenres,

            mood:
                mood,

            rating:
                rating,

            year_min:
                yearMin,

            year_max:
                yearMaxValue

                    ? Number(
                        yearMaxValue
                    )

                    : null,

            runtime_max:
                runtimeValue

                    ? Number(
                        runtimeValue
                    )

                    : null,

            language:
                language,

            popularity_mode:
                popularityMode,

            era_preference:
                eraPreference,

            reference_movie:
                referenceMovie
                || null,

            avoid_genres:
                avoidGenres,

            results_limit:
                resultsLimit

        };


        console.log(
            "Preferências enviadas:",
            preferences
        );


        moviesContainer.innerHTML = `

            <p class="empty-message">

                🧠 Analisando filmes e calculando compatibilidade...

            </p>

        `;


        recommendationSummary.innerHTML =
            "";


        recommendButton.disabled =
            true;


        recommendButton.textContent =
            "Calculando recomendações...";


        try {


            const response =
                await fetch(

                    "http://127.0.0.1:8000/recommendations",

                    {

                        method:
                            "POST",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body:
                            JSON.stringify(
                                preferences
                            )

                    }

                );


            const data =
                await response.json();


            if (
                !response.ok
            ) {

                throw new Error(

                    data.detail
                    ||
                    "Erro ao gerar recomendações."

                );

            }


            currentMovies =
                data.movies;


            if (
                currentMovies.length === 0
            ) {

                moviesContainer.innerHTML = `

                    <p class="empty-message">

                        😕 Nenhum filme encontrado.
                        Tente reduzir os filtros.

                    </p>

                `;

                return;

            }


            let summary = `

                ${data.total_candidates}
                filmes analisados.

            `;


            if (
                data.reference_movie
            ) {

                summary += `

                    Filme de referência:
                    <strong>
                        ${data.reference_movie.title}
                    </strong>.

                `;

            }


            recommendationSummary.innerHTML =
                summary;


            showMovies(
                currentMovies
            );


        }

        catch (
            error
        ) {


            console.error(
                error
            );


            moviesContainer.innerHTML = `

                <p class="empty-message">

                    ❌ ${error.message}

                </p>

            `;


        }

        finally {


            recommendButton.disabled =
                false;


            recommendButton.textContent =
                "Encontrar filmes para mim";

        }

    }
);



/* =====================================================
   CARDS
===================================================== */

function showMovies(
    movieList
) {


    moviesContainer.innerHTML =
        "";


    movieList.forEach(

        function (
            movie,
            index
        ) {


            const genresHTML =
                movie.genres

                    .map(

                        genre => `

                            <span class="genre">
                                ${genre}
                            </span>

                        `

                    )

                    .join("");


            const poster =
                movie.poster
                ||
                "https://placehold.co/500x750?text=Sem+Poster";


            const card =
                document.createElement(
                    "article"
                );


            card.classList.add(
                "movie-card"
            );


            card.innerHTML = `

                <div class="poster-container">

                    <img
                        class="movie-poster"
                        src="${poster}"
                        alt="Pôster de ${movie.title}"
                        loading="lazy"
                    >

                    <span class="compatibility">

                        ${movie.compatibility}%

                    </span>

                </div>


                <div class="movie-info">

                    <h3 class="movie-title">
                        ${movie.title}
                    </h3>


                    <div class="movie-metadata">

                        <span class="movie-rating">
                            ⭐ ${movie.rating}
                        </span>

                        <span>
                            📅 ${movie.year || "—"}
                        </span>

                    </div>


                    <div class="movie-genres">
                        ${genresHTML}
                    </div>


                    <button
                        class="details-button"
                        data-index="${index}"
                    >
                        Ver detalhes
                    </button>

                </div>

            `;


            moviesContainer.appendChild(
                card
            );

        }

    );


    addDetailsEvents();

}



/* =====================================================
   DETALHES
===================================================== */

function addDetailsEvents() {


    const buttons =
        document.querySelectorAll(
            ".details-button"
        );


    buttons.forEach(

        function (
            button
        ) {


            button.addEventListener(

                "click",

                function () {


                    const index =
                        Number(
                            button.dataset.index
                        );


                    openMovieModal(

                        currentMovies[
                            index
                        ]

                    );

                }

            );

        }

    );

}



/* =====================================================
   MODAL
===================================================== */

async function openMovieModal(
    movie
) {


    const genresHTML =
        movie.genres

            .map(

                genre => `

                    <span class="genre">
                        ${genre}
                    </span>

                `

            )

            .join("");


    const poster =
        movie.poster
        ||
        "https://placehold.co/500x750?text=Sem+Poster";


    const description =
        movie.description
        ||
        "Sinopse não disponível em português.";


    const reasonsHTML =
        movie.reasons.length

            ? movie.reasons
                .map(
                    reason => `
                        <li>
                            ${reason}
                        </li>
                    `
                )
                .join("")

            : `
                <li>
                    Compatibilidade calculada a partir das suas preferências.
                </li>
            `;


    const breakdownHTML =
        Object.entries(
            movie.breakdown
        )

        .map(

            ([name, score]) => `

                <span class="score-item">

                    ${name}:
                    ${score.points}/${score.max}

                </span>

            `

        )

        .join("");


    modalMovieContent.innerHTML = `

        <div class="modal-movie">


            <div>

                <img
                    class="modal-poster"
                    src="${poster}"
                    alt="Pôster de ${movie.title}"
                >

            </div>


            <div class="modal-info">


                <h2>
                    ${movie.title}
                </h2>


                <div class="modal-metadata">

                    <span>
                        ⭐ ${movie.rating}
                    </span>

                    <span>
                        📅 ${movie.year || "—"}
                    </span>

                    <span>
                        🟢 ${movie.compatibility}% compatível
                    </span>

                </div>


                <div class="modal-genres">
                    ${genresHTML}
                </div>


                <div class="modal-synopsis">

                    <h3>
                        Sinopse
                    </h3>

                    <p>
                        ${description}
                    </p>

                </div>


                <div class="match-reasons">

                    <h3>
                        🧠 Por que recomendamos?
                    </h3>

                    <ul>
                        ${reasonsHTML}
                    </ul>

                    <div class="score-breakdown">

                        ${breakdownHTML}

                    </div>

                </div>


                <div
                    class="watch-section"
                    id="watchSection"
                >

                    <h3>
                        🇧🇷 Onde assistir no Brasil
                    </h3>

                    <div class="providers-loading">
                        ⏳ Buscando plataformas...
                    </div>

                </div>


            </div>

        </div>

    `;


    movieModal.classList.add(
        "active"
    );


    document.body.style.overflow =
        "hidden";


    await loadWatchProviders(
        movie.id
    );

}



/* =====================================================
   STREAMING
===================================================== */

async function loadWatchProviders(
    movieId
) {


    const watchSection =
        document.getElementById(
            "watchSection"
        );


    try {


        const response =
            await fetch(

                `http://127.0.0.1:8000/movies/${movieId}/watch-providers`

            );


        const data =
            await response.json();


        if (
            !data.available
        ) {


            watchSection.innerHTML = `

                <h3>
                    🇧🇷 Onde assistir no Brasil
                </h3>

                <span class="not-available">

                    Nenhuma opção encontrada
                    atualmente para o Brasil.

                </span>

                <p class="watch-attribution">

                    Dados fornecidos pelo JustWatch
                    através do TMDB.

                </p>

            `;


            return;

        }


        const streamingHTML =
            createProviderList(
                data.streaming
            );


        const rentHTML =
            createProviderList(
                data.rent
            );


        const buyHTML =
            createProviderList(
                data.buy
            );


        const linkHTML =
            data.link

                ? `

                    <a
                        class="watch-link"
                        href="${data.link}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Ver mais opções ↗
                    </a>

                `

                : "";


        watchSection.innerHTML = `

            <h3>
                🇧🇷 Onde assistir no Brasil
            </h3>


            <div class="watch-type">

                <strong>
                    ▶ Streaming por assinatura
                </strong>

                <div class="providers-list">
                    ${streamingHTML}
                </div>

            </div>


            <div class="watch-type">

                <strong>
                    🔑 Alugar
                </strong>

                <div class="providers-list">
                    ${rentHTML}
                </div>

            </div>


            <div class="watch-type">

                <strong>
                    🛒 Comprar
                </strong>

                <div class="providers-list">
                    ${buyHTML}
                </div>

            </div>


            ${linkHTML}


            <p class="watch-attribution">

                Dados fornecidos pelo JustWatch
                através do TMDB.

            </p>

        `;


    }

    catch (
        error
    ) {


        watchSection.innerHTML = `

            <h3>
                🇧🇷 Onde assistir no Brasil
            </h3>

            <span class="not-available">

                Não foi possível consultar
                as plataformas agora.

            </span>

        `;

    }

}



/* =====================================================
   PROVIDERS
===================================================== */

function createProviderList(
    providers
) {


    if (
        !providers
        ||
        providers.length === 0
    ) {

        return `

            <span class="not-available">
                Não disponível
            </span>

        `;

    }


    return providers

        .map(

            provider => `

                <div class="provider-card">

                    ${
                        provider.logo

                            ? `

                                <img
                                    class="provider-logo"
                                    src="${provider.logo}"
                                    alt="${provider.name}"
                                >

                            `

                            : ""
                    }

                    <span class="provider-name">
                        ${provider.name}
                    </span>

                </div>

            `

        )

        .join("");

}



/* =====================================================
   FECHAR
===================================================== */

function hideModal() {

    movieModal.classList.remove(
        "active"
    );

    document.body.style.overflow =
        "";

}


closeModal.addEventListener(
    "click",
    hideModal
);


movieModal.addEventListener(

    "click",

    function (
        event
    ) {

        if (
            event.target
            ===
            movieModal
        ) {

            hideModal();

        }

    }

);


document.addEventListener(

    "keydown",

    function (
        event
    ) {

        if (
            event.key === "Escape"
        ) {

            hideModal();

        }

    }

);