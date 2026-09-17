"""Topic extraction enrichment."""


class TopicExtractor:
    """Extracts high-level topical categories and keywords from document sections."""

    def extract_topics(self, text: str, title: str | None = None) -> list[str]:
        topics = []
        if title:
            topics.append(title)
        # Extract potential keyword topics
        words = [w.lower().strip(".,;:\"'()") for w in text.split() if len(w) > 4]
        word_freq: dict[str, int] = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1

        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        topics.extend([w for w, count in top_words if count > 1])
        return list(dict.fromkeys(topics))
