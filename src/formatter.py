from __future__ import annotations

import os
import re
from datetime import date

from src.models import Comment, Post


class Formatter:
    def to_markdown(
        self,
        subreddit_data: dict[str, list[Post]],
        comments: dict[str, list[Comment]],
        meta: dict,
    ) -> str:
        lines: list[str] = []

        lines.append("# Reddit Research Dump")
        lines.append("")
        lines.append(f"**Niche:** {meta['niche']}")
        lines.append(f"**Date:** {meta['date']}")
        lines.append(f"**Subreddits:** {', '.join(meta['subreddits'])}")
        lines.append(f"**Total posts:** {meta['post_count']}")
        lines.append("")

        for subreddit, posts in subreddit_data.items():
            lines.append(f"## r/{subreddit}")
            lines.append("")

            for post in posts:
                lines.append(f"### {post.title} ({post.upvotes} upvotes)")
                lines.append("")
                if post.body:
                    lines.append(post.body)
                    lines.append("")
                post_comments = comments.get(post.id, [])
                if post_comments:
                    for comment in post_comments:
                        lines.append(f"- **{comment.upvotes}** {comment.body}")
                    lines.append("")

        return "\n".join(lines)

    def save(self, content: str, output_dir: str, niche: str) -> str:
        slug = self._slugify(niche)
        filename = f"{date.today().isoformat()}_{slug}.md"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    @staticmethod
    def _slugify(text: str) -> str:
        text = text.lower()
        text = text.replace(" ", "_")
        text = re.sub(r"[^a-z0-9_]", "", text)
        return text
