"""
Fixed taxonomy for AI tagging — strict vocabulary.
AI will ONLY choose from these categories.
"""

TAXONOMY = {
    "Security": ["CyberSecurity", "Privacy", "Vulnerability"],
    "Dev": ["WebDev", "MobileDev", "DevOps", "Cloud"],
    "Data/AI": ["AI", "ML", "Data"],
    "Business": ["FinTech", "Startups", "BigTech"],
    "Infra": ["Databases", "Networking", "Hardware"],
    "Misc": ["GeneralTech", "Others"],
}

# Flat list of all allowed tags
ALL_TAGS: list[str] = []
for category_tags in TAXONOMY.values():
    ALL_TAGS.extend(category_tags)

# Tag → Parent Category mapping
TAG_TO_CATEGORY: dict[str, str] = {}
for category, tag_list in TAXONOMY.items():
    for tag in tag_list:
        TAG_TO_CATEGORY[tag] = category

# Sentiment options
SENTIMENTS = ["Positive", "Negative", "Neutral"]
