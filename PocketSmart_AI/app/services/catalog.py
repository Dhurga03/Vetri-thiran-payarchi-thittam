from urllib.parse import quote_plus


PLATFORM_URLS = {

    "Amazon":
        "https://www.amazon.in/s?k={q}",

    "Flipkart":
        "https://www.flipkart.com/search?q={q}",

    "IKEA":
        "https://www.ikea.com/in/en/search/?q={q}",

    "Swiggy":
        "https://www.swiggy.com/search?query={q}",

    "Zomato":
        "https://www.zomato.com/search?query={q}",

    "OYO":
        "https://www.oyorooms.com/search?q={q}"
}


def create_platform_links(
    query: str,
    platforms: list[str]
):

    encoded_query = quote_plus(
        query
    )


    links = []


    for platform in platforms:

        if platform not in PLATFORM_URLS:

            continue


        links.append(
            {
                "platform": platform,

                "url": PLATFORM_URLS[
                    platform
                ].format(
                    q=encoded_query
                )
            }
        )


    return links