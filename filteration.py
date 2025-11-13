def classify_article(article):
    """
    article = string containing title + description + content
    returns: "REMOVE", "IMPORTANT", "NOT IMPORTANT", or "NEUTRAL"
    """

    text = article.lower()

    # ----------------------------
    # 1. Filter OUT non-US content
    # ----------------------------
    non_us_keywords = [
        "china", "india", "russia", "uk", "england", "europe", "africa",
        "asia", "middle east", "mexico", "canada", "brazil", "australia",
        "japan", "south america", "international", "global"
    ]

    for k in non_us_keywords:
        if k in text:
            return "REMOVE"

    # ----------------------------
    # 2. Filter OUT political content
    # ----------------------------
    political_keywords = [
        "election", "vote", "ballot", "president", "senator", "governor",
        "congress", "parliament", "policy", "bill", "legislation",
        "democrat", "republican", "campaign", "white house", "supreme court",
        "lawmaker", "administration"
    ]

    for k in political_keywords:
        if k in text:
            return "REMOVE"

    # ----------------------------
    # 3. Classify IMPORTANT articles
    # ----------------------------
    important_keywords = [
        "breaking", "urgent", "emergency", "crisis", "public safety",
        "severe weather", "health advisory", "recall", "missing person",
        "natural disaster", "major update"
    ]

    for k in important_keywords:
        if k in text:
            return "IMPORTANT"

    # ----------------------------
    # 4. Classify NOT IMPORTANT articles
    # ----------------------------
    not_important_keywords = [
        "celebrity", "gossip", "viral", "meme", "influencer",
        "entertainment", "fashion", "sports rumor", "pop culture"
    ]

    for k in not_important_keywords:
        if k in text:
            return "NOT IMPORTANT"

    # ----------------------------
    # 5. Everything else = Neutral
    # ----------------------------
    return "NEUTRAL"
