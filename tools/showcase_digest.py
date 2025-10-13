#!/usr/bin/env python3
"""
Generate showcase digest with one news from each category.

This tool creates a daily showcase digest featuring the best news
from each category (crypto, sports, markets, tech, world).
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime

from digests.generator import generate_digest

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def generate_showcase():
    """Generate showcase digest for all categories."""
    categories = ["crypto", "sports", "markets", "tech", "world"]
    showcase = {}

    logger.info("🎯 Starting showcase digest generation...")

    for category in categories:
        logger.info(f"🔄 Generating digest for {category}...")

        try:
            digest = await generate_digest(
                limit=1,  # One news per category
                category=category,
                ai=True,
                style="newsroom",  # Use newsroom style for consistency
                tone="neutral",
                length="short",
                audience="general",
                use_v2=True
            )

            showcase[category] = digest
            logger.info(f"✅ {category} digest generated")

        except Exception as e:
            logger.error(f"❌ Failed to generate digest for {category}: {e}")
            showcase[category] = f"Ошибка генерации дайджеста для категории {category}: {str(e)}"

    # Save to static/showcase.json
    output_path = Path(__file__).parent.parent / "static" / "showcase.json"
    output_path.parent.mkdir(exist_ok=True)

    # Add metadata
    showcase_data = {
        "generated_at": datetime.now().isoformat(),
        "categories": showcase,
        "total_categories": len(categories),
        "successful_generations": len([d for d in showcase.values() if not d.startswith("Ошибка")])
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(showcase_data, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ Showcase saved to {output_path}")

    # Print markdown summary
    print("\n" + "="*60)
    print("📰 DIGEST OF THE DAY")
    print("="*60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Categories: {showcase_data['successful_generations']}/{showcase_data['total_categories']}")
    print("="*60)

    for category, digest in showcase.items():
        print(f"\n**{category.upper()}**")
        print("-" * 20)
        if digest.startswith("Ошибка"):
            print(f"❌ {digest}")
        else:
            # Truncate for display
            display_text = digest[:300] + "..." if len(digest) > 300 else digest
            print(display_text)

    print("\n" + "="*60)
    print("✅ Showcase generation completed!")
    print("="*60)

    return showcase_data


async def main():
    """Main function."""
    try:
        showcase_data = await generate_showcase()

        # Return success status
        successful = showcase_data['successful_generations']
        total = showcase_data['total_categories']

        if successful == total:
            logger.info("🎉 All categories generated successfully!")
            return 0
        elif successful > 0:
            logger.warning(f"⚠️ Partial success: {successful}/{total} categories generated")
            return 1
        else:
            logger.error("❌ All categories failed to generate")
            return 2

    except Exception as e:
        logger.error(f"❌ Showcase generation failed: {e}")
        return 3


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
