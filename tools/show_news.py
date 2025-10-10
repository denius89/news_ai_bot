#!/usr/bin/env python3
"""
CLI утилита для тестирования AI Digest Journalistic System v2.

Использование:
    python tools/show_news.py --category tech --ai --style analytical --tone insightful --length medium
    python tools/show_news.py --category crypto --ai --style newsroom --tone neutral --length short --use-v2
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from digests.generator import generate_digest


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Generate AI digest with v2 journalistic system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate tech digest with analytical style
  python tools/show_news.py --category tech --ai --style analytical --tone insightful --length medium
  
  # Generate crypto digest with newsroom style (v2)
  python tools/show_news.py --category crypto --ai --style newsroom --tone neutral --length short --use-v2
  
  # Generate business digest with magazine style
  python tools/show_news.py --category markets --ai --style magazine --tone optimistic --length long --audience pro
  
  # Submit feedback for a digest
  python tools/show_news.py --feedback 0.9 --digest-id "uuid-here"
        """
    )
    
    # Basic arguments
    parser.add_argument("--category", default="tech", 
                       choices=["crypto", "markets", "tech", "sports", "world"],
                       help="News category (default: tech)")
    parser.add_argument("--ai", action="store_true", 
                       help="Use AI summarization")
    parser.add_argument("--limit", type=int, default=10, 
                       help="Number of news items (default: 10)")
    
    # Style arguments
    parser.add_argument("--style", default="analytical",
                       choices=["analytical", "business", "meme", "newsroom", "magazine", "casual"],
                       help="Digest style (default: analytical)")
    parser.add_argument("--tone", default="neutral",
                       choices=["neutral", "insightful", "critical", "optimistic"],
                       help="Digest tone (default: neutral)")
    parser.add_argument("--length", default="medium",
                       choices=["short", "medium", "long"],
                       help="Digest length (default: medium)")
    parser.add_argument("--audience", default="general",
                       choices=["general", "pro"],
                       help="Target audience (default: general)")
    
    # Version control
    parser.add_argument("--use-v2", action="store_true",
                       help="Use v2 journalistic prompts")
    parser.add_argument("--legacy", action="store_true",
                       help="Force legacy generation (disable v2)")
    
    # Output options
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--json", action="store_true",
                       help="Output raw JSON (v2 only)")
    
    # Feedback options
    parser.add_argument("--feedback", type=float, metavar="SCORE",
                       help="Submit feedback score (0.0-1.0)")
    parser.add_argument("--digest-id", type=str,
                       help="Digest ID for feedback submission")
    
    args = parser.parse_args()
    
    # Determine v2 usage
    use_v2 = args.use_v2 and not args.legacy
    
    if args.verbose:
        print("🔍 Configuration:")
        print(f"  Category: {args.category}")
        print(f"  Style: {args.style}")
        print(f"  Tone: {args.tone}")
        print(f"  Length: {args.length}")
        print(f"  Audience: {args.audience}")
        print(f"  AI: {args.ai}")
        print(f"  V2: {use_v2}")
        print(f"  Limit: {args.limit}")
        print()
    
    try:
        # Generate digest
        digest = await generate_digest(
            limit=args.limit,
            category=args.category,
            ai=args.ai,
            style=args.style,
            tone=args.tone,
            length=args.length,
            audience=args.audience,
            use_v2=use_v2
        )
        
        if args.json and use_v2:
            # For v2, we might want to show raw JSON
            print("📄 Raw JSON output:")
            print(digest)
        else:
            # Regular text output
            print("📰 Generated Digest:")
            print("=" * 50)
            print(digest)
            print("=" * 50)
            
            if args.verbose:
                print(f"\n✅ Digest generated successfully")
                print(f"📊 Length: {len(digest)} characters")
        
        # Handle feedback submission
        if args.feedback is not None and args.digest_id:
            try:
                import requests
                
                if not 0.0 <= args.feedback <= 1.0:
                    print(f"❌ Feedback score must be between 0.0 and 1.0, got: {args.feedback}")
                    sys.exit(1)
                
                response = requests.post(
                    "http://localhost:8001/api/feedback",
                    json={"digest_id": args.digest_id, "score": args.feedback},
                    timeout=10
                )
                
                if response.ok:
                    print("✅ Feedback submitted successfully")
                else:
                    print(f"❌ Failed to submit feedback: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Network error submitting feedback: {e}")
            except Exception as e:
                print(f"❌ Error submitting feedback: {e}")
        
    except Exception as e:
        print(f"❌ Error generating digest: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
