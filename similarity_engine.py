def calculate_similarity(
    user_title,
    user_topic,
    user_subtopic,
    user_intent,
    benchmark_video
):

    score = 0

    if benchmark_video.get("topic") == user_topic:
        score += 40

    if benchmark_video.get("intent") == user_intent:
        score += 20

    user_words = set(user_title.lower().split())

    candidate_words = set(
        benchmark_video["title"].lower().split()
    )

    overlap = len(
        user_words.intersection(candidate_words)
    )

    score += min(overlap * 5, 25)

    if benchmark_video.get("format") == benchmark_video.get("user_format"):
        score += 15

    return min(score, 100)


def rank_benchmarks(
    user_title,
    topic,
    subtopic,
    intent,
    benchmark_results
):

    videos = (
        benchmark_results["peers"] +
        benchmark_results["elites"]
    )

    ranked = []

    for video in videos:

        video["similarity_score"] = calculate_similarity(
            user_title,
            topic,
            subtopic,
            intent,
            video
        )

        ranked.append(video)

    ranked.sort(
        key=lambda x: x["similarity_score"],
        reverse=True
    )

    return ranked[:10]