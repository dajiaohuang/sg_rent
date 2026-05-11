from app.config import settings


def normalize_min_max(values: list[float]) -> list[float]:
    """Normalize values to [0, 1] where lower is better (inverted)."""
    if len(values) <= 1:
        return [0.5] * len(values)
    vmin, vmax = min(values), max(values)
    if vmin == vmax:
        return [0.5] * len(values)
    # Invert: lower original value -> higher normalized score
    return [(vmax - v) / (vmax - vmin) for v in values]


def amenity_score(amenities: list[str] | None) -> float:
    """Calculate amenity score from 0 to 1."""
    if not amenities:
        return 0.0
    weights = {
        "pool": 0.15, "gym": 0.12, "bbq": 0.08, "tennis": 0.08,
        "function_room": 0.05, "sauna": 0.07, "jacuzzi": 0.06,
        "sky_garden": 0.07, "clubhouse": 0.05, "yoga_deck": 0.05,
        "reading_room": 0.03, "basketball": 0.05, "steam_room": 0.05,
        "market": 0.08, "food_court": 0.08, "coffee_shop": 0.06,
        "playground": 0.04, "park": 0.06, "clinic": 0.05,
        "community_club": 0.04, "sports_complex": 0.06, "library": 0.05,
        "convenience_store": 0.03,
        "fully_furnished": 0.05, "partial_furnished": 0.02,
    }
    score = sum(weights.get(a, 0.02) for a in amenities)
    return min(score, 1.0)


def rank_properties(
    properties: list[dict],
    weights: dict[str, float] | None = None,
) -> list[dict]:
    """
    Rank properties by weighted score.
    Each property dict must have: 'commute_time' (float or None), 'monthly_rent', 'amenities'.
    Properties with None commute_time get score 0 and are sorted to the bottom.
    """
    w = weights or {
        "commute": settings.commute_weight,
        "price": settings.price_weight,
        "amenity": settings.amenity_weight,
    }

    valid = [p for p in properties if p.get("commute_time") is not None]
    invalid = [p for p in properties if p.get("commute_time") is None]

    for p in invalid:
        p["score"] = 0.0

    if not valid:
        return invalid

    commute_times = [p["commute_time"] for p in valid]
    prices = [p["monthly_rent"] for p in valid]

    norm_commute = normalize_min_max(commute_times)
    norm_price = normalize_min_max(prices)

    for i, p in enumerate(valid):
        amen = amenity_score(p.get("amenities"))
        p["score"] = (
            w["commute"] * norm_commute[i]
            + w["price"] * norm_price[i]
            + w["amenity"] * amen
        )

    for p in invalid:
        p["score"] = 0.0

    valid.sort(key=lambda x: x["score"], reverse=True)
    return valid + invalid
