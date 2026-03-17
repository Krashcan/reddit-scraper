import os
from datetime import date

from src.formatter import Formatter
from src.models import Comment, Post

# --- Fixture data ---

SAMPLE_POSTS = [
    Post(
        id="abc123",
        title="I built a SaaS in 30 days",
        body="Here is my journey building a marketing tool...",
        url="https://www.reddit.com/r/SideProject/comments/abc123/",
        upvotes=542,
        subreddit="SideProject",
        num_comments=87,
    ),
    Post(
        id="def456",
        title="How I got my first 100 users",
        body="",
        url="https://www.reddit.com/r/SideProject/comments/def456/",
        upvotes=210,
        subreddit="SideProject",
        num_comments=32,
    ),
]

SAMPLE_COMMENTS = {
    "abc123": [
        Comment(id="com1", body="Great work!", upvotes=34, post_id="abc123"),
        Comment(
            id="com2",
            body="How did you market it?",
            upvotes=21,
            post_id="abc123",
        ),
    ],
    "def456": [
        Comment(
            id="com3", body="Love this!", upvotes=12, post_id="def456"
        ),
    ],
}

SAMPLE_META = {
    "niche": "marketing for engineers",
    "date": "2026-03-17",
    "subreddits": ["SideProject"],
    "post_count": 2,
}


# --- to_markdown ---


class TestToMarkdown:
    def setup_method(self):
        self.formatter = Formatter()
        self.output = self.formatter.to_markdown(
            subreddit_data={"SideProject": SAMPLE_POSTS},
            comments=SAMPLE_COMMENTS,
            meta=SAMPLE_META,
        )

    def test_starts_with_research_dump_heading(self):
        assert self.output.startswith("# Reddit Research Dump")

    def test_header_contains_niche(self):
        lines = self.output.split("\n")
        header = "\n".join(lines[:10])
        assert "marketing for engineers" in header

    def test_header_contains_date(self):
        lines = self.output.split("\n")
        header = "\n".join(lines[:10])
        assert "2026-03-17" in header

    def test_header_contains_subreddits(self):
        lines = self.output.split("\n")
        header = "\n".join(lines[:10])
        assert "SideProject" in header

    def test_header_contains_post_count(self):
        lines = self.output.split("\n")
        header = "\n".join(lines[:10])
        assert "2" in header

    def test_subreddit_has_h2_heading(self):
        assert "## r/SideProject" in self.output

    def test_post_title_appears_as_h3_with_upvotes(self):
        assert "### I built a SaaS in 30 days" in self.output
        assert "542" in self.output

    def test_post_body_appears_when_nonempty(self):
        assert "Here is my journey building a marketing tool..." in self.output

    def test_comments_rendered_as_bullet_points(self):
        assert "- Great work!" in self.output or "- **34** Great work!" in self.output

    def test_comment_upvotes_shown(self):
        assert "34" in self.output
        assert "21" in self.output

    def test_post_with_no_body_renders_cleanly(self):
        # Find the section for the second post
        idx = self.output.index("How I got my first 100 users")
        # There should be no blank body section between title and comments
        section = self.output[idx : idx + 200]
        assert "\n\n\n\n" not in section


# --- save ---


class TestSave:
    def test_saves_file_to_disk(self, tmp_path):
        formatter = Formatter()
        content = "# Test content"
        formatter.save(content, str(tmp_path), "general")

        files = os.listdir(tmp_path)
        assert len(files) == 1
        assert files[0].endswith(".md")

    def test_filename_matches_date_niche_pattern(self, tmp_path):
        formatter = Formatter()
        content = "# Test content"
        formatter.save(content, str(tmp_path), "marketing for engineers")

        files = os.listdir(tmp_path)
        today = date.today().isoformat()
        expected = f"{today}_marketing_for_engineers.md"
        assert files[0] == expected

    def test_niche_slugified_lowercase(self, tmp_path):
        formatter = Formatter()
        formatter.save("content", str(tmp_path), "Marketing For Engineers")

        files = os.listdir(tmp_path)
        assert "marketing_for_engineers" in files[0]

    def test_niche_slugified_spaces_to_underscores(self, tmp_path):
        formatter = Formatter()
        formatter.save("content", str(tmp_path), "side project ideas")

        files = os.listdir(tmp_path)
        assert "side_project_ideas" in files[0]
        assert " " not in files[0]

    def test_niche_slugified_special_chars_removed(self, tmp_path):
        formatter = Formatter()
        formatter.save("content", str(tmp_path), "marketing! & engineers?")

        files = os.listdir(tmp_path)
        filename = files[0]
        assert "!" not in filename
        assert "&" not in filename
        assert "?" not in filename

    def test_file_content_matches_input(self, tmp_path):
        formatter = Formatter()
        content = "# Reddit Research Dump\nSome content here"
        formatter.save(content, str(tmp_path), "test")

        files = os.listdir(tmp_path)
        filepath = tmp_path / files[0]
        assert filepath.read_text() == content
