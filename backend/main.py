import os

from typing import List, Optional

import httpx

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    HTTPException
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from pydantic import (
    BaseModel,
    Field
)


# =========================================================
# CONFIGURAÇÃO
# =========================================================

load_dotenv()


app = FastAPI(
    title="MovieMatch API",
    description="Sistema personalizado de recomendação de filmes",
    version="3.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


TMDB_TOKEN = os.getenv("TMDB_TOKEN")


TMDB_BASE_URL = (
    "https://api.themoviedb.org/3"
)


TMDB_IMAGE_URL = (
    "https://image.tmdb.org/t/p/w500"
)


TMDB_PROVIDER_IMAGE_URL = (
    "https://image.tmdb.org/t/p/w92"
)


HEADERS = {

    "Authorization":
        f"Bearer {TMDB_TOKEN}",

    "accept":
        "application/json"

}


# =========================================================
# GÊNEROS
# =========================================================

GENRE_IDS = {

    "acao": 28,
    "aventura": 12,
    "animacao": 16,
    "comedia": 35,
    "crime": 80,
    "documentario": 99,
    "drama": 18,
    "familia": 10751,
    "fantasia": 14,
    "ficcao": 878,
    "misterio": 9648,
    "romance": 10749,
    "terror": 27,
    "thriller": 53

}


# =========================================================
# HUMOR
# =========================================================

MOOD_GENRES = {

    "rir": [
        35,
        10751,
        16
    ],

    "pensar": [
        878,
        9648,
        18
    ],

    "adrenalina": [
        28,
        12,
        53
    ],

    "emocionar": [
        18,
        10749,
        16
    ],

    "tensao": [
        53,
        27,
        80,
        9648
    ],

    "leve": [
        35,
        10751,
        16,
        10749
    ],

    "surpreender": [
        9648,
        878,
        53
    ]

}


MOOD_LABELS = {

    "rir":
        "humor e leveza",

    "pensar":
        "filmes mais reflexivos",

    "adrenalina":
        "ação e adrenalina",

    "emocionar":
        "carga emocional",

    "tensao":
        "tensão e suspense",

    "leve":
        "uma experiência mais leve",

    "surpreender":
        "mistério e surpresa"

}


# =========================================================
# MODELO
# =========================================================

class Preferences(BaseModel):

    genres: List[str]

    mood: str

    rating: float

    year_min: int

    year_max: Optional[int] = None

    runtime_max: Optional[int] = None

    language: str = "any"

    popularity_mode: str = "balanced"

    era_preference: str = "any"

    reference_movie: Optional[str] = None

    avoid_genres: List[str] = Field(
        default_factory=list
    )

    results_limit: int = 20


# =========================================================
# TOKEN
# =========================================================

def check_token():

    if not TMDB_TOKEN:

        raise HTTPException(
            status_code=500,
            detail="TMDB_TOKEN não encontrado."
        )


# =========================================================
# HELPERS
# =========================================================

def clamp(
    value,
    minimum=0,
    maximum=1
):

    return max(
        minimum,
        min(
            value,
            maximum
        )
    )


async def get_genre_map(
    client
):

    url = (
        f"{TMDB_BASE_URL}"
        f"/genre/movie/list"
    )


    response = await client.get(

        url,

        headers=HEADERS,

        params={
            "language":
                "pt-BR"
        }

    )


    response.raise_for_status()


    data = response.json()


    return {

        genre["id"]:
            genre["name"]

        for genre
        in data.get(
            "genres",
            []
        )

    }


# =========================================================
# FILME DE REFERÊNCIA
# =========================================================

async def resolve_reference_movie(
    client,
    title
):

    if not title:

        return None


    title = title.strip()


    if not title:

        return None


    search_response = await client.get(

        f"{TMDB_BASE_URL}/search/movie",

        headers=HEADERS,

        params={

            "query":
                title,

            "language":
                "pt-BR",

            "region":
                "BR",

            "include_adult":
                "false",

            "page":
                1

        }

    )


    search_response.raise_for_status()


    results = (
        search_response
        .json()
        .get(
            "results",
            []
        )
    )


    if not results:

        return None


    reference = results[0]


    recommended_ids = set()


    for page in range(
        1,
        3
    ):

        response = await client.get(

            (
                f"{TMDB_BASE_URL}"
                f"/movie/{reference['id']}"
                f"/recommendations"
            ),

            headers=HEADERS,

            params={

                "language":
                    "pt-BR",

                "page":
                    page

            }

        )


        if response.status_code == 200:

            recommendation_data = (
                response.json()
            )


            for movie in recommendation_data.get(
                "results",
                []
            ):

                movie_id = movie.get(
                    "id"
                )


                if movie_id:

                    recommended_ids.add(
                        movie_id
                    )


    return {

        "id":
            reference.get("id"),

        "title":
            reference.get("title"),

        "genre_ids":
            set(
                reference.get(
                    "genre_ids",
                    []
                )
            ),

        "recommended_ids":
            recommended_ids

    }


# =========================================================
# ÉPOCA
# =========================================================

def calculate_era_score(
    year,
    era
):

    if not year:

        return 0


    if era == "recent":

        if year >= 2020:
            return 10

        if year >= 2015:
            return 7

        if year >= 2010:
            return 4

        return 1


    if era == "2010s":

        if 2010 <= year <= 2019:
            return 10

        distance = min(
            abs(year - 2010),
            abs(year - 2019)
        )

        return max(
            0,
            10 - distance
        )


    if era == "2000s":

        if 2000 <= year <= 2009:
            return 10

        distance = min(
            abs(year - 2000),
            abs(year - 2009)
        )

        return max(
            0,
            10 - distance
        )


    if era == "classics":

        if year < 1990:
            return 10

        if year < 2000:
            return 6

        if year < 2010:
            return 3

        return 0


    return 0


# =========================================================
# SCORE
# =========================================================

def calculate_compatibility(
    movie,
    preferences,
    selected_genres,
    mood_genres,
    popularity_percentile,
    reference
):

    movie_genres = set(
        movie.get(
            "genre_ids",
            []
        )
    )


    raw_score = 0.0

    maximum_score = 0.0

    breakdown = {}

    reasons = []


    # =====================================================
    # 1. GÊNEROS
    # 30 pontos
    # =====================================================

    genre_max = 30

    maximum_score += genre_max


    matches = len(

        movie_genres.intersection(
            selected_genres
        )

    )


    genre_ratio = (

        matches
        /
        len(selected_genres)

    )


    genre_points = (
        genre_ratio
        *
        genre_max
    )


    raw_score += genre_points


    breakdown["Gêneros"] = {

        "points":
            round(
                genre_points,
                1
            ),

        "max":
            genre_max

    }


    if (
        matches
        ==
        len(selected_genres)
    ):

        reasons.append(

            (
                "Possui todos os "
                f"{len(selected_genres)} "
                "gêneros que você selecionou."
            )

        )


    # =====================================================
    # 2. HUMOR
    # 15 pontos
    # =====================================================

    mood_max = 15

    maximum_score += mood_max


    mood_matches = len(

        movie_genres.intersection(
            mood_genres
        )

    )


    if mood_matches >= 2:

        mood_points = 15


    elif mood_matches == 1:

        mood_points = 8


    else:

        mood_points = 0


    raw_score += mood_points


    breakdown["Humor"] = {

        "points":
            mood_points,

        "max":
            mood_max

    }


    if mood_matches:

        reasons.append(

            "Combina com sua preferência por "
            +
            MOOD_LABELS.get(
                preferences.mood,
                "esse tipo de experiência"
            )
            +
            "."

        )


    # =====================================================
    # 3. NOTA
    # 15 pontos
    # =====================================================

    quality_max = 15

    maximum_score += quality_max


    rating = movie.get(
        "vote_average",
        0
    )


    quality_ratio = clamp(

        (
            rating - 5
        )
        /
        4.5

    )


    quality_points = (

        quality_ratio
        *
        quality_max

    )


    raw_score += quality_points


    breakdown["Nota"] = {

        "points":
            round(
                quality_points,
                1
            ),

        "max":
            quality_max

    }


    if rating >= 8:

        reasons.append(

            f"Possui nota alta no TMDB: {rating:.1f}."

        )


    # =====================================================
    # 4. POPULARIDADE
    # 10 pontos
    # =====================================================

    popularity_max = 10

    maximum_score += popularity_max


    if (
        preferences.popularity_mode
        ==
        "popular"
    ):

        popularity_ratio = (
            popularity_percentile
        )


    elif (
        preferences.popularity_mode
        ==
        "hidden"
    ):

        popularity_ratio = (
            1
            -
            popularity_percentile
        )


    else:

        popularity_ratio = (

            1
            -
            abs(
                popularity_percentile
                -
                0.55
            )
            /
            0.55

        )


        popularity_ratio = clamp(
            popularity_ratio
        )


    popularity_points = (

        popularity_ratio
        *
        popularity_max

    )


    raw_score += popularity_points


    breakdown["Descoberta"] = {

        "points":
            round(
                popularity_points,
                1
            ),

        "max":
            popularity_max

    }


    # =====================================================
    # 5. FILME DE REFERÊNCIA
    # =====================================================

    if reference:

        reference_max = 25

        maximum_score += reference_max


        reference_points = 0


        if (
            movie.get("id")
            in
            reference[
                "recommended_ids"
            ]
        ):

            reference_points += 15


        reference_genres = (
            reference[
                "genre_ids"
            ]
        )


        union = (
            movie_genres
            |
            reference_genres
        )


        intersection = (
            movie_genres
            &
            reference_genres
        )


        if union:

            similarity = (

                len(intersection)
                /
                len(union)

            )


            reference_points += (

                similarity
                *
                10

            )


        reference_points = min(
            reference_points,
            reference_max
        )


        raw_score += (
            reference_points
        )


        breakdown[
            "Filme de referência"
        ] = {

            "points":
                round(
                    reference_points,
                    1
                ),

            "max":
                reference_max

        }


        if reference_points >= 12:

            reasons.append(

                (
                    "Tem forte relação com "
                    f"“{reference['title']}”."
                )

            )


    # =====================================================
    # 6. IDIOMA
    # =====================================================

    if (
        preferences.language
        !=
        "any"
    ):

        language_max = 5

        maximum_score += language_max


        if (
            movie.get(
                "original_language"
            )
            ==
            preferences.language
        ):

            language_points = 5

        else:

            language_points = 0


        raw_score += (
            language_points
        )


        breakdown["Idioma"] = {

            "points":
                language_points,

            "max":
                language_max

        }


        if language_points:

            reasons.append(
                "Está no idioma original que você prefere."
            )


    # =====================================================
    # 7. ÉPOCA
    # =====================================================

    if (
        preferences.era_preference
        !=
        "any"
    ):

        era_max = 10

        maximum_score += era_max


        release_date = movie.get(
            "release_date",
            ""
        )


        try:

            movie_year = int(
                release_date[:4]
            )

        except (
            ValueError,
            TypeError
        ):

            movie_year = None


        era_points = (
            calculate_era_score(
                movie_year,
                preferences.era_preference
            )
        )


        raw_score += (
            era_points
        )


        breakdown["Época"] = {

            "points":
                era_points,

            "max":
                era_max

        }


        if era_points >= 8:

            reasons.append(
                "O ano de lançamento combina com a época que você prefere."
            )


    # =====================================================
    # NORMALIZAÇÃO
    # =====================================================

    compatibility = round(

        (
            raw_score
            /
            maximum_score
        )
        *
        100

    )


    compatibility = max(
        0,
        min(
            compatibility,
            100
        )
    )


    return (
        compatibility,
        breakdown,
        reasons
    )


# =========================================================
# FORMATAR FILME
# =========================================================

def format_movie(
    movie,
    genre_map,
    compatibility,
    breakdown,
    reasons
):

    poster_path = movie.get(
        "poster_path"
    )


    poster = None


    if poster_path:

        poster = (
            f"{TMDB_IMAGE_URL}"
            f"{poster_path}"
        )


    release_date = movie.get(
        "release_date",
        ""
    )


    year = (
        release_date[:4]
        if release_date
        else None
    )


    genres = [

        genre_map[
            genre_id
        ]

        for genre_id
        in movie.get(
            "genre_ids",
            []
        )

        if genre_id
        in genre_map

    ]


    return {

        "id":
            movie.get("id"),

        "title":
            movie.get("title"),

        "original_title":
            movie.get(
                "original_title"
            ),

        "rating":
            round(
                movie.get(
                    "vote_average",
                    0
                ),
                1
            ),

        "year":
            year,

        "release_date":
            release_date,

        "genres":
            genres,

        "description":
            movie.get(
                "overview"
            ),

        "poster":
            poster,

        "popularity":
            movie.get(
                "popularity",
                0
            ),

        "vote_count":
            movie.get(
                "vote_count",
                0
            ),

        "compatibility":
            compatibility,

        "breakdown":
            breakdown,

        "reasons":
            reasons

    }


# =========================================================
# PROVIDER
# =========================================================

def format_provider(
    provider
):

    logo_path = provider.get(
        "logo_path"
    )


    logo = None


    if logo_path:

        logo = (
            f"{TMDB_PROVIDER_IMAGE_URL}"
            f"{logo_path}"
        )


    return {

        "id":
            provider.get(
                "provider_id"
            ),

        "name":
            provider.get(
                "provider_name"
            ),

        "logo":
            logo,

        "priority":
            provider.get(
                "display_priority",
                999
            )

    }


# =========================================================
# HOME
# =========================================================

@app.get("/")
async def home():

    return {

        "message":
            "MovieMatch API funcionando!",

        "version":
            "3.1.0"

    }


# =========================================================
# RECOMENDAÇÕES
# =========================================================

@app.post(
    "/recommendations"
)
async def recommendations(
    preferences: Preferences
):

    check_token()


    selected_genres = [

        GENRE_IDS[genre]

        for genre
        in preferences.genres

        if genre
        in GENRE_IDS

    ]


    if not selected_genres:

        raise HTTPException(
            status_code=400,
            detail="Selecione pelo menos um gênero válido."
        )


    avoid_genres = [

        GENRE_IDS[genre]

        for genre
        in preferences.avoid_genres

        if genre
        in GENRE_IDS

    ]


    mood_genres = (
        MOOD_GENRES.get(
            preferences.mood,
            []
        )
    )


    # =====================================================
    # IMPORTANTE
    #
    # VÍRGULA = AND
    #
    # Exemplo:
    #
    # 28,10749
    #
    # significa:
    #
    # Ação E Romance
    # =====================================================

    genre_filter = ",".join(

        str(genre_id)

        for genre_id
        in selected_genres

    )


    avoid_filter = ",".join(

        str(genre_id)

        for genre_id
        in avoid_genres

    )


    if (
        preferences.popularity_mode
        ==
        "popular"
    ):

        sort_by = (
            "popularity.desc"
        )


    elif (
        preferences.popularity_mode
        ==
        "hidden"
    ):

        sort_by = (
            "vote_average.desc"
        )


    else:

        sort_by = (
            "vote_count.desc"
        )


    try:

        async with httpx.AsyncClient(
            timeout=30
        ) as client:


            genre_map = await get_genre_map(
                client
            )


            reference = (
                await resolve_reference_movie(

                    client,

                    preferences.reference_movie

                )
            )


            all_movies = []


            for page in range(
                1,
                6
            ):


                params = {

                    "language":
                        "pt-BR",

                    "region":
                        "BR",

                    "page":
                        page,

                    "with_genres":
                        genre_filter,

                    "vote_average.gte":
                        preferences.rating,

                    "vote_count.gte":
                        80,

                    "primary_release_date.gte":
                        (
                            f"{preferences.year_min}"
                            "-01-01"
                        ),

                    "sort_by":
                        sort_by,

                    "include_adult":
                        "false",

                    "include_video":
                        "false"

                }


                if (
                    preferences.year_max
                ):

                    params[
                        "primary_release_date.lte"
                    ] = (

                        f"{preferences.year_max}"
                        "-12-31"

                    )


                if (
                    preferences.runtime_max
                ):

                    params[
                        "with_runtime.lte"
                    ] = (
                        preferences.runtime_max
                    )


                if avoid_filter:

                    params[
                        "without_genres"
                    ] = avoid_filter


                response = await client.get(

                    (
                        f"{TMDB_BASE_URL}"
                        f"/discover/movie"
                    ),

                    headers=HEADERS,

                    params=params

                )


                response.raise_for_status()


                data = response.json()


                all_movies.extend(

                    data.get(
                        "results",
                        []
                    )

                )


    except httpx.HTTPStatusError as error:

        raise HTTPException(

            status_code=
                error.response.status_code,

            detail=
                error.response.text

        )


    except httpx.RequestError as error:

        raise HTTPException(

            status_code=500,

            detail=(
                "Erro ao conectar ao TMDB: "
                +
                str(error)
            )

        )


    # =====================================================
    # DEDUPLICAR
    # =====================================================

    unique_movies = {}


    for movie in all_movies:

        movie_id = movie.get(
            "id"
        )


        if movie_id:

            unique_movies[
                movie_id
            ] = movie


    candidate_movies = list(
        unique_movies.values()
    )


    # =====================================================
    # SEGUNDA VALIDAÇÃO LOCAL
    #
    # Mesmo que o TMDB filtre,
    # nós validamos novamente.
    #
    # O filme PRECISA ter TODOS
    # os gêneros selecionados.
    # =====================================================

    required_genres = set(
        selected_genres
    )


    candidate_movies = [

        movie

        for movie
        in candidate_movies

        if required_genres.issubset(

            set(
                movie.get(
                    "genre_ids",
                    []
                )
            )

        )

    ]


    # =====================================================
    # REMOVER FILME REFERÊNCIA
    # =====================================================

    if reference:

        candidate_movies = [

            movie

            for movie
            in candidate_movies

            if movie.get(
                "id"
            )
            !=
            reference["id"]

        ]


    # =====================================================
    # POPULARIDADE
    # =====================================================

    popularity_sorted = sorted(

        candidate_movies,

        key=lambda movie:
            movie.get(
                "popularity",
                0
            )

    )


    popularity_percentiles = {}


    total_popularity = len(
        popularity_sorted
    )


    for index, movie in enumerate(
        popularity_sorted
    ):

        if total_popularity <= 1:

            percentile = 0.5

        else:

            percentile = (

                index
                /
                (
                    total_popularity
                    -
                    1
                )

            )


        popularity_percentiles[
            movie["id"]
        ] = percentile


    # =====================================================
    # SCORE
    # =====================================================

    scored_movies = []


    for movie in candidate_movies:


        if not movie.get(
            "poster_path"
        ):

            continue


        if not movie.get(
            "overview"
        ):

            continue


        percentile = (
            popularity_percentiles.get(
                movie["id"],
                0.5
            )
        )


        (
            compatibility,
            breakdown,
            reasons

        ) = calculate_compatibility(

            movie,

            preferences,

            selected_genres,

            mood_genres,

            percentile,

            reference

        )


        scored_movies.append(

            format_movie(

                movie,

                genre_map,

                compatibility,

                breakdown,

                reasons

            )

        )


    # =====================================================
    # ORDENAR
    # =====================================================

    scored_movies.sort(

        key=lambda movie: (

            movie[
                "compatibility"
            ],

            movie[
                "rating"
            ],

            movie[
                "vote_count"
            ]

        ),

        reverse=True

    )


    limit = max(
        5,
        min(
            preferences.results_limit,
            20
        )
    )


    final_movies = (
        scored_movies[:limit]
    )


    return {

        "algorithm_version":
            "3.1",

        "genre_matching":
            "AND",

        "required_genres":
            [

                genre_map.get(
                    genre_id
                )

                for genre_id
                in selected_genres

            ],

        "total_candidates":
            len(candidate_movies),

        "total":
            len(final_movies),

        "reference_movie":

            {

                "id":
                    reference["id"],

                "title":
                    reference["title"]

            }

            if reference

            else None,

        "movies":
            final_movies

    }


# =========================================================
# STREAMING
# =========================================================

@app.get(
    "/movies/{movie_id}/watch-providers"
)
async def get_watch_providers(
    movie_id: int
):

    check_token()


    url = (

        f"{TMDB_BASE_URL}"
        f"/movie/{movie_id}"
        f"/watch/providers"

    )


    try:

        async with httpx.AsyncClient(
            timeout=20
        ) as client:


            response = await client.get(
                url,
                headers=HEADERS
            )


            response.raise_for_status()


    except httpx.HTTPStatusError as error:

        raise HTTPException(

            status_code=
                error.response.status_code,

            detail=
                error.response.text

        )


    except httpx.RequestError as error:

        raise HTTPException(

            status_code=500,

            detail=str(error)

        )


    brazil = (

        response
        .json()
        .get(
            "results",
            {}
        )
        .get(
            "BR"
        )

    )


    if not brazil:

        return {

            "available":
                False,

            "streaming":
                [],

            "rent":
                [],

            "buy":
                [],

            "link":
                None

        }


    def get_list(
        key
    ):

        providers = [

            format_provider(
                provider
            )

            for provider
            in brazil.get(
                key,
                []
            )

        ]


        providers.sort(

            key=lambda provider:
                provider["priority"]

        )


        return providers


    return {

        "available":
            True,

        "streaming":
            get_list(
                "flatrate"
            ),

        "rent":
            get_list(
                "rent"
            ),

        "buy":
            get_list(
                "buy"
            ),

        "link":
            brazil.get(
                "link"
            )

    }