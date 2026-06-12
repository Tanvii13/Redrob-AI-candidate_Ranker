def build_candidate_text(candidate):

    text = ""

    profile = candidate["profile"]

    text += profile["headline"] + " "
    text += profile["summary"] + " "

    for job in candidate["career_history"]:

        text += (
            job["title"]
            + " "
            + job["description"]
            + " "
        )

    for skill in candidate["skills"]:

        text += skill["name"] + " "

    return text