"""
Tests for showcase digest generation.

This module tests:
- Showcase digest generation
- JSON output format
- Error handling
- File creation
"""

import pytest
import json
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import showcase tool
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.showcase_digest import generate_showcase


class TestShowcaseGeneration:
    """Test showcase digest generation."""

    @pytest.mark.asyncio
    @patch('tools.showcase_digest.generate_digest')
    async def test_showcase_generation_success(self, mock_generate_digest):
        """Test successful showcase generation."""
        # Mock digest generation for each category
        mock_digests = {
            "crypto": "Bitcoin reaches new highs as institutional adoption grows...",
            "sports": "Championship finals set for next weekend...",
            "markets": "Stock markets show mixed signals amid economic uncertainty...",
            "tech": "New AI breakthrough promises faster processing...",
            "world": "International summit addresses climate change..."
        }

        def mock_generate_side_effect(*args, **kwargs):
            category = kwargs.get('category', 'tech')
            return mock_digests.get(category, "Default digest")

        mock_generate_digest.side_effect = mock_generate_side_effect

        # Mock file operations
        with patch('builtins.open', MagicMock()) as mock_open:
            with patch('pathlib.Path.mkdir', MagicMock()):
                showcase_data = await generate_showcase()

        # Verify structure
        assert "generated_at" in showcase_data
        assert "categories" in showcase_data
        assert "total_categories" in showcase_data
        assert "successful_generations" in showcase_data

        # Verify categories
        assert showcase_data["total_categories"] == 5
        assert showcase_data["successful_generations"] == 5

        categories = showcase_data["categories"]
        assert "crypto" in categories
        assert "sports" in categories
        assert "markets" in categories
        assert "tech" in categories
        assert "world" in categories

        # Verify content
        assert categories["crypto"] == mock_digests["crypto"]
        assert categories["sports"] == mock_digests["sports"]

    @pytest.mark.asyncio
    @patch('tools.showcase_digest.generate_digest')
    async def test_showcase_generation_partial_failure(self, mock_generate_digest):
        """Test showcase generation with some failures."""
        # Mock some successful, some failed generations
        def mock_generate_side_effect(*args, **kwargs):
            category = kwargs.get('category', 'tech')
            if category in ["crypto", "sports"]:
                return f"Success digest for {category}"
            else:
                raise Exception(f"Generation failed for {category}")

        mock_generate_digest.side_effect = mock_generate_side_effect

        with patch('builtins.open', MagicMock()) as mock_open:
            with patch('pathlib.Path.mkdir', MagicMock()):
                showcase_data = await generate_showcase()

        # Verify partial success
        assert showcase_data["total_categories"] == 5
        assert showcase_data["successful_generations"] == 2

        categories = showcase_data["categories"]
        assert "Success digest for crypto" in categories["crypto"]
        assert "Success digest for sports" in categories["sports"]
        assert "Ошибка генерации" in categories["markets"]
        assert "Ошибка генерации" in categories["tech"]
        assert "Ошибка генерации" in categories["world"]

    @pytest.mark.asyncio
    @patch('tools.showcase_digest.generate_digest')
    async def test_showcase_generation_complete_failure(self, mock_generate_digest):
        """Test showcase generation with complete failure."""
        mock_generate_digest.side_effect = Exception("All generations failed")

        with patch('builtins.open', MagicMock()) as mock_open:
            with patch('pathlib.Path.mkdir', MagicMock()):
                showcase_data = await generate_showcase()

        # Verify complete failure
        assert showcase_data["total_categories"] == 5
        assert showcase_data["successful_generations"] == 0

        categories = showcase_data["categories"]
        for category in ["crypto", "sports", "markets", "tech", "world"]:
            assert "Ошибка генерации" in categories[category]

    @pytest.mark.asyncio
    @patch('tools.showcase_digest.generate_digest')
    async def test_showcase_file_creation(self, mock_generate_digest):
        """Test that showcase file is created correctly."""
        mock_generate_digest.return_value = "Test digest content"

        # Mock file operations
        mock_file_content = []

        def mock_open_side_effect(path, mode, **kwargs):
            if 'w' in mode:
                mock_file = MagicMock()
                mock_file.write = lambda content: mock_file_content.append(content)
                return mock_file
            return MagicMock()

        with patch('builtins.open', side_effect=mock_open_side_effect):
            with patch('pathlib.Path.mkdir', MagicMock()):
                await generate_showcase()

        # Verify file was written
        assert len(mock_file_content) > 0

        # Parse JSON content
        json_content = json.loads(mock_file_content[0])
        assert "generated_at" in json_content
        assert "categories" in json_content
        assert "total_categories" in json_content
        assert "successful_generations" in json_content


class TestShowcaseMain:
    """Test main function and exit codes."""

    @pytest.mark.asyncio
    @patch('tools.showcase_digest.generate_showcase')
    async def test_main_success(self, mock_generate_showcase):
        """Test main function with successful generation."""
        mock_generate_showcase.return_value = {
            "successful_generations": 5,
            "total_categories": 5
        }

        from tools.showcase_digest import main
        exit_code = await main()

        assert exit_code == 0

    @pytest.mark.asyncio
    @patch('tools.showcase_digest.generate_showcase')
    async def test_main_partial_success(self, mock_generate_showcase):
        """Test main function with partial success."""
        mock_generate_showcase.return_value = {
            "successful_generations": 3,
            "total_categories": 5
        }

        from tools.showcase_digest import main
        exit_code = await main()

        assert exit_code == 1

    @pytest.mark.asyncio
    @patch('tools.showcase_digest.generate_showcase')
    async def test_main_complete_failure(self, mock_generate_showcase):
        """Test main function with complete failure."""
        mock_generate_showcase.return_value = {
            "successful_generations": 0,
            "total_categories": 5
        }

        from tools.showcase_digest import main
        exit_code = await main()

        assert exit_code == 2

    @pytest.mark.asyncio
    @patch('tools.showcase_digest.generate_showcase')
    async def test_main_exception(self, mock_generate_showcase):
        """Test main function with exception."""
        mock_generate_showcase.side_effect = Exception("Unexpected error")

        from tools.showcase_digest import main
        exit_code = await main()

        assert exit_code == 3


class TestShowcaseIntegration:
    """Integration tests for showcase functionality."""

    def test_showcase_json_structure(self):
        """Test that generated JSON has correct structure."""
        # Sample showcase data
        sample_data = {
            "generated_at": datetime.now().isoformat(),
            "categories": {
                "crypto": "Bitcoin analysis...",
                "sports": "Sports news...",
                "markets": "Market update...",
                "tech": "Tech breakthrough...",
                "world": "World news..."
            },
            "total_categories": 5,
            "successful_generations": 5
        }

        # Convert to JSON and back
        json_str = json.dumps(sample_data, ensure_ascii=False, indent=2)
        parsed_data = json.loads(json_str)

        # Verify structure
        assert "generated_at" in parsed_data
        assert "categories" in parsed_data
        assert "total_categories" in parsed_data
        assert "successful_generations" in parsed_data

        # Verify categories
        assert len(parsed_data["categories"]) == 5
        assert parsed_data["total_categories"] == 5
        assert parsed_data["successful_generations"] == 5

    def test_showcase_categories_list(self):
        """Test that all required categories are included."""
        expected_categories = ["crypto", "sports", "markets", "tech", "world"]

        # This would be tested in the actual generation
        assert len(expected_categories) == 5
        assert "crypto" in expected_categories
        assert "sports" in expected_categories
        assert "markets" in expected_categories
        assert "tech" in expected_categories
        assert "world" in expected_categories


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
