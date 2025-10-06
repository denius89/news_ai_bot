#!/usr/bin/env python3
"""
Baseline Dataset Builder for PulseAI Self-Tuning Predictor.

This tool creates a comprehensive baseline dataset by combining
internal PulseAI data with external open datasets for training
the Self-Tuning Predictor models.
"""

import sys
import csv
import json
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter

import pandas as pd
import yaml

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_modules.metrics import get_metrics

logger = logging.getLogger("baseline_dataset_builder")


class BaselineDatasetBuilder:
    """
    Builds a comprehensive baseline dataset for Self-Tuning Predictor.

    Combines internal PulseAI data with external open datasets
    to create a balanced training dataset.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize dataset builder with configuration."""
        self.config = self._load_config(config_path)
        self.output_dir = Path("data")
        self.output_dir.mkdir(exist_ok=True)

        self.dataset_path = self.output_dir / "pulseai_dataset.csv"
        self.report_path = self.output_dir / "dataset_report.json"
        self.backup_path = self.output_dir / "pulseai_dataset_backup.csv"

        # Configuration parameters
        self.config_section = self.config.get("dataset_builder", {})
        self.external_sources = self.config_section.get("external_sources", {})
        self.balance_classes = self.config_section.get("balance_classes", True)
        self.min_title_length = self.config_section.get("min_title_length", 5)
        self.min_samples_per_class = self.config_section.get("min_samples_per_class", 500)
        self.save_report = self.config_section.get("save_report", True)

        # Metrics
        self.metrics = get_metrics()

        # Statistics tracking
        self.stats = {
            "total_samples": 0,
            "positive_samples": 0,
            "negative_samples": 0,
            "internal_sources": 0,
            "external_sources": 0,
            "duplicates_removed": 0,
            "avg_importance": 0.0,
            "avg_credibility": 0.0,
            "sources": {},
            "categories": {},
        }

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "ai_optimization.yaml"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def _load_prefilter_rules(self) -> Dict[str, List[str]]:
        """Load prefilter rules for noise filtering."""
        try:
            rules_path = Path(__file__).parent.parent / "config" / "prefilter_rules.yaml"
            with open(rules_path, "r", encoding="utf-8") as f:
                rules = yaml.safe_load(f) or {}

            return {
                "stop_markers": rules.get("stop_markers", []),
                "auto_stop_markers": [
                    item.get("word", "") for item in rules.get("auto_generated", {}).get("stop_markers", [])
                ],
                "source_blacklist": [
                    item.get("source", "") for item in rules.get("auto_generated", {}).get("source_blacklist", [])
                ],
            }
        except Exception as e:
            logger.warning(f"Error loading prefilter rules: {e}")
            return {"stop_markers": [], "auto_stop_markers": [], "source_blacklist": []}

    def _create_backup(self) -> None:
        """Create backup of existing dataset."""
        if self.dataset_path.exists():
            try:
                import shutil

                shutil.copy2(self.dataset_path, self.backup_path)
                logger.info(f"Backup created: {self.backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")

    def _load_internal_data(self) -> List[Dict[str, Any]]:
        """
        Load internal data from database and logs.

        Returns:
            List of internal data samples
        """
        samples = []

        try:
            # Load from database
            db_samples = self._load_database_data()
            samples.extend(db_samples)
            self.stats["internal_sources"] += len(db_samples)

            # Load from rejected log
            rejected_samples = self._load_rejected_log_data()
            samples.extend(rejected_samples)
            self.stats["internal_sources"] += len(rejected_samples)

            logger.info(f"Loaded {len(samples)} internal samples")

        except Exception as e:
            logger.error(f"Error loading internal data: {e}")

        return samples

    def _load_database_data(self) -> List[Dict[str, Any]]:
        """Load data from database."""
        samples = []

        try:
            from database.service import get_sync_service

            db_service = get_sync_service()
            news_items = db_service.get_latest_news(limit=5000)

            for item in news_items:
                # Convert to dict if needed
                if hasattr(item, "model_dump"):
                    item_dict = item.model_dump()
                elif hasattr(item, "dict"):
                    item_dict = item.dict()
                else:
                    item_dict = dict(item)

                title = item_dict.get("title", "")
                if len(title.split()) < self.min_title_length:
                    continue

                importance = item_dict.get("importance", 0.0)
                credibility = item_dict.get("credibility", 0.0)

                # Create binary label based on thresholds
                label = 1 if importance >= 0.6 and credibility >= 0.7 else 0

                sample = {
                    "title": title,
                    "category": item_dict.get("category", "unknown"),
                    "source": item_dict.get("source", "unknown"),
                    "importance": importance,
                    "credibility": credibility,
                    "label": label,
                    "data_source": "database",
                }

                samples.append(sample)

            logger.info(f"Loaded {len(samples)} samples from database")

        except Exception as e:
            logger.error(f"Error loading database data: {e}")

        return samples

    def _load_rejected_log_data(self) -> List[Dict[str, Any]]:
        """Load data from rejected log."""
        samples = []

        rejected_log_path = Path("logs/rejected.log")
        if not rejected_log_path.exists():
            logger.warning("rejected.log not found")
            return samples

        try:
            with open(rejected_log_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or not line.startswith("["):
                        continue

                    try:
                        # Parse log line
                        parsed = self._parse_rejected_log_line(line)
                        if parsed:
                            title = parsed.get("title", "")
                            if len(title.split()) < self.min_title_length:
                                continue

                            sample = {
                                "title": title,
                                "category": parsed.get("category", "unknown"),
                                "source": parsed.get("source", "unknown"),
                                "importance": 0.0,  # Rejected items are low importance
                                "credibility": 0.0,  # Rejected items are low credibility
                                "label": 0,  # Rejected items are negative
                                "data_source": "rejected_log",
                            }

                            samples.append(sample)

                    except Exception as e:
                        logger.warning(f"Error parsing rejected log line {line_num}: {e}")
                        continue

            logger.info(f"Loaded {len(samples)} samples from rejected log")

        except Exception as e:
            logger.error(f"Error loading rejected log: {e}")

        return samples

    def _parse_rejected_log_line(self, line: str) -> Optional[Dict]:
        """Parse a rejected log line."""
        try:
            import re

            # Extract timestamp
            timestamp_match = re.match(r"\[([^\]]+)\]", line)
            if not timestamp_match:
                return None

            timestamp = timestamp_match.group(1)

            # Extract key-value pairs after "REJECTED:"
            if "REJECTED:" not in line:
                return None

            data_part = line.split("REJECTED:", 1)[1].strip()

            # Parse key-value pairs
            data = {}
            for pair in data_part.split():
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    value = value.strip("\"'")
                    data[key] = value

            # Extract title from the end if present
            title_match = re.search(r'title="([^"]+)"', line)
            if title_match:
                data["title"] = title_match.group(1)

            data["timestamp"] = timestamp
            return data

        except Exception as e:
            logger.debug(f"Error parsing log line: {e}")
            return None

    def _load_external_data(self) -> List[Dict[str, Any]]:
        """
        Load external datasets from various sources.

        Returns:
            List of external data samples
        """
        samples = []

        # Load fake news dataset
        if self.external_sources.get("fake_news", True):
            fake_news_samples = self._load_fake_news_dataset()
            samples.extend(fake_news_samples)

        # Load news category dataset
        if self.external_sources.get("news_category", True):
            news_category_samples = self._load_news_category_dataset()
            samples.extend(news_category_samples)

        # Load crypto headlines
        if self.external_sources.get("crypto_headlines", True):
            crypto_samples = self._load_crypto_headlines_dataset()
            samples.extend(crypto_samples)

        # Load AG News dataset
        if self.external_sources.get("ag_news", False):
            ag_news_samples = self._load_ag_news_dataset()
            samples.extend(ag_news_samples)

        self.stats["external_sources"] = len(samples)
        logger.info(f"Loaded {len(samples)} external samples")

        return samples

    def _load_fake_news_dataset(self) -> List[Dict[str, Any]]:
        """Load fake news dataset (simulated)."""
        samples = []

        try:
            # Simulate fake news dataset loading
            # In real implementation, this would load from Kaggle API or downloaded file

            fake_samples = [
                {
                    "title": "Breaking: Scientists discover cure for all diseases",
                    "category": "world",
                    "source": "fake-news-site.com",
                    "importance": 0.2,
                    "credibility": 0.1,
                    "label": 0,
                    "data_source": "fake_news_dataset",
                },
                {
                    "title": "Official statement from government on new policy",
                    "category": "world",
                    "source": "government.gov",
                    "importance": 0.8,
                    "credibility": 0.9,
                    "label": 1,
                    "data_source": "fake_news_dataset",
                },
            ]

            samples.extend(fake_samples)
            logger.info(f"Loaded {len(samples)} samples from fake news dataset")

        except Exception as e:
            logger.warning(f"⚠️ Skipped external dataset (fake_news): {e}")

        return samples

    def _load_news_category_dataset(self) -> List[Dict[str, Any]]:
        """Load news category dataset (simulated)."""
        samples = []

        try:
            # Simulate news category dataset loading

            category_samples = [
                {
                    "title": "Bitcoin reaches new all-time high amid institutional adoption",
                    "category": "crypto",
                    "source": "coindesk.com",
                    "importance": 0.85,
                    "credibility": 0.8,
                    "label": 1,
                    "data_source": "news_category_dataset",
                },
                {
                    "title": "Apple announces new iPhone with advanced AI features",
                    "category": "tech",
                    "source": "apple.com",
                    "importance": 0.9,
                    "credibility": 0.95,
                    "label": 1,
                    "data_source": "news_category_dataset",
                },
            ]

            samples.extend(category_samples)
            logger.info(f"Loaded {len(samples)} samples from news category dataset")

        except Exception as e:
            logger.warning(f"⚠️ Skipped external dataset (news_category): {e}")

        return samples

    def _load_crypto_headlines_dataset(self) -> List[Dict[str, Any]]:
        """Load crypto headlines dataset (simulated)."""
        samples = []

        try:
            # Simulate crypto headlines dataset loading

            crypto_samples = [
                {
                    "title": "Ethereum 2.0 upgrade completes successfully",
                    "category": "crypto",
                    "source": "ethereum.org",
                    "importance": 0.9,
                    "credibility": 0.9,
                    "label": 1,
                    "data_source": "crypto_headlines_dataset",
                },
                {
                    "title": "Free Bitcoin giveaway - click here now!",
                    "category": "crypto",
                    "source": "bitcoin-giveaway.fake",
                    "importance": 0.1,
                    "credibility": 0.1,
                    "label": 0,
                    "data_source": "crypto_headlines_dataset",
                },
            ]

            samples.extend(crypto_samples)
            logger.info(f"Loaded {len(samples)} samples from crypto headlines dataset")

        except Exception as e:
            logger.warning(f"⚠️ Skipped external dataset (crypto_headlines): {e}")

        return samples

    def _load_ag_news_dataset(self) -> List[Dict[str, Any]]:
        """Load AG News dataset (simulated)."""
        samples = []

        try:
            # Simulate AG News dataset loading

            ag_samples = [
                {
                    "title": "Stock market shows strong performance in Q4",
                    "category": "markets",
                    "source": "bloomberg.com",
                    "importance": 0.7,
                    "credibility": 0.8,
                    "label": 1,
                    "data_source": "ag_news_dataset",
                }
            ]

            samples.extend(ag_samples)
            logger.info(f"Loaded {len(samples)} samples from AG News dataset")

        except Exception as e:
            logger.warning(f"⚠️ Skipped external dataset (ag_news): {e}")

        return samples

    def _clean_and_normalize_data(self, samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and normalize the dataset.

        Args:
            samples: Raw samples

        Returns:
            Cleaned and normalized samples
        """
        logger.info("Cleaning and normalizing data...")

        # Load prefilter rules
        prefilter_rules = self._load_prefilter_rules()
        stop_markers = prefilter_rules["stop_markers"] + prefilter_rules["auto_stop_markers"]
        source_blacklist = prefilter_rules["source_blacklist"]

        cleaned_samples = []
        seen_titles = set()

        for sample in samples:
            title = sample.get("title", "").strip()
            source = sample.get("source", "").strip().lower()

            # Skip empty titles
            if not title:
                continue

            # Skip titles that are too short
            if len(title.split()) < self.min_title_length:
                continue

            # Skip blacklisted sources
            if any(blacklisted in source for blacklisted in source_blacklist):
                continue

            # Skip titles with stop markers
            title_lower = title.lower()
            if any(marker in title_lower for marker in stop_markers):
                continue

            # Remove duplicates based on title
            title_key = title.lower().strip()
            if title_key in seen_titles:
                self.stats["duplicates_removed"] += 1
                continue
            seen_titles.add(title_key)

            # Normalize title
            sample["title"] = title.strip()

            # Normalize category
            category = sample.get("category", "unknown").lower()
            sample["category"] = self._normalize_category(category)

            # Normalize source
            sample["source"] = source

            cleaned_samples.append(sample)

        logger.info(
            f"Cleaned data: {len(cleaned_samples)} samples (removed {len(samples) - len(cleaned_samples)} samples)"
        )

        return cleaned_samples

    def _normalize_category(self, category: str) -> str:
        """Normalize category to standard categories."""
        category_lower = category.lower()

        # Map to standard categories
        category_mapping = {
            "technology": "tech",
            "sports": "sports",
            "business": "markets",
            "finance": "markets",
            "economy": "markets",
            "politics": "world",
            "world": "world",
            "international": "world",
            "crypto": "crypto",
            "cryptocurrency": "crypto",
            "bitcoin": "crypto",
            "ethereum": "crypto",
            "blockchain": "crypto",
        }

        return category_mapping.get(category_lower, "unknown")

    def _balance_dataset(self, samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Balance the dataset classes.

        Args:
            samples: List of samples

        Returns:
            Balanced dataset
        """
        if not self.balance_classes:
            return samples

        logger.info("Balancing dataset classes...")

        # Separate positive and negative samples
        positive_samples = [s for s in samples if s.get("label", 0) == 1]
        negative_samples = [s for s in samples if s.get("label", 0) == 0]

        logger.info(f"Before balancing: {len(positive_samples)} positive, {len(negative_samples)} negative")

        # Check if we have enough samples per class
        if len(positive_samples) < self.min_samples_per_class:
            logger.warning(f"Not enough positive samples: {len(positive_samples)} < {self.min_samples_per_class}")
        if len(negative_samples) < self.min_samples_per_class:
            logger.warning(f"Not enough negative samples: {len(negative_samples)} < {self.min_samples_per_class}")

        # Balance by undersampling the larger class
        if len(positive_samples) > len(negative_samples):
            # Undersample positive samples
            import random

            random.seed(42)  # For reproducibility
            positive_samples = random.sample(positive_samples, len(negative_samples))
        elif len(negative_samples) > len(positive_samples):
            # Undersample negative samples
            import random

            random.seed(42)  # For reproducibility
            negative_samples = random.sample(negative_samples, len(positive_samples))

        balanced_samples = positive_samples + negative_samples

        logger.info(f"After balancing: {len(positive_samples)} positive, {len(negative_samples)} negative")

        return balanced_samples

    def _calculate_statistics(self, samples: List[Dict[str, Any]]) -> None:
        """Calculate dataset statistics."""
        self.stats["total_samples"] = len(samples)
        self.stats["positive_samples"] = sum(1 for s in samples if s.get("label", 0) == 1)
        self.stats["negative_samples"] = sum(1 for s in samples if s.get("label", 0) == 0)

        # Calculate averages
        importance_values = [s.get("importance", 0.0) for s in samples if s.get("importance", 0.0) > 0]
        credibility_values = [s.get("credibility", 0.0) for s in samples if s.get("credibility", 0.0) > 0]

        self.stats["avg_importance"] = sum(importance_values) / len(importance_values) if importance_values else 0.0
        self.stats["avg_credibility"] = sum(credibility_values) / len(credibility_values) if credibility_values else 0.0

        # Count sources and categories
        sources = Counter(s.get("source", "unknown") for s in samples)
        categories = Counter(s.get("category", "unknown") for s in samples)

        self.stats["sources"] = dict(sources.most_common(10))
        self.stats["categories"] = dict(categories.most_common())

    def _save_dataset(self, samples: List[Dict[str, Any]]) -> None:
        """Save dataset to CSV file."""
        logger.info(f"Saving dataset to {self.dataset_path}")

        try:
            with open(self.dataset_path, "w", newline="", encoding="utf-8") as f:
                if samples:
                    fieldnames = ["title", "category", "source", "importance", "credibility", "label"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for sample in samples:
                        row = {
                            "title": sample.get("title", ""),
                            "category": sample.get("category", "unknown"),
                            "source": sample.get("source", "unknown"),
                            "importance": sample.get("importance", 0.0),
                            "credibility": sample.get("credibility", 0.0),
                            "label": sample.get("label", 0),
                        }
                        writer.writerow(row)

            logger.info(f"Dataset saved successfully: {len(samples)} samples")

        except Exception as e:
            logger.error(f"Error saving dataset: {e}")
            raise

    def _save_report(self) -> None:
        """Save dataset report to JSON file."""
        if not self.save_report:
            return

        logger.info(f"Saving report to {self.report_path}")

        try:
            report = {"timestamp": datetime.now(timezone.utc).isoformat(), **self.stats}

            with open(self.report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info("Report saved successfully")

        except Exception as e:
            logger.error(f"Error saving report: {e}")

    def build_dataset(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Build the complete baseline dataset.

        Args:
            dry_run: If True, don't save files, just return statistics

        Returns:
            Dictionary with build results and statistics
        """
        logger.info("Starting baseline dataset build...")

        if not dry_run:
            self._create_backup()

        try:
            # Load internal data
            internal_samples = self._load_internal_data()

            # Load external data
            external_samples = self._load_external_data()

            # Combine all samples
            all_samples = internal_samples + external_samples

            logger.info(f"Total samples collected: {len(all_samples)}")

            # Clean and normalize
            cleaned_samples = self._clean_and_normalize_data(all_samples)

            # Balance dataset
            balanced_samples = self._balance_dataset(cleaned_samples)

            # Calculate statistics
            self._calculate_statistics(balanced_samples)

            # Save dataset and report
            if not dry_run:
                self._save_dataset(balanced_samples)
                self._save_report()

                # Update metrics
                self.metrics.increment_dataset_created_total()

            # Print summary
            self._print_summary()

            result = {
                "success": True,
                "total_samples": self.stats["total_samples"],
                "positive_samples": self.stats["positive_samples"],
                "negative_samples": self.stats["negative_samples"],
                "internal_sources": self.stats["internal_sources"],
                "external_sources": self.stats["external_sources"],
                "duplicates_removed": self.stats["duplicates_removed"],
                "avg_importance": self.stats["avg_importance"],
                "avg_credibility": self.stats["avg_credibility"],
                "dataset_path": str(self.dataset_path),
                "report_path": str(self.report_path),
            }

            logger.info("Baseline dataset build completed successfully")
            return result

        except Exception as e:
            logger.error(f"Error building dataset: {e}")
            return {"success": False, "error": str(e), "total_samples": 0}

    def _print_summary(self) -> None:
        """Print dataset summary to console."""
        print("\n" + "=" * 60)
        print("📊 BASELINE DATASET SUMMARY")
        print("=" * 60)
        print(f"Total samples: {self.stats['total_samples']}")
        print(f"Positive samples: {self.stats['positive_samples']}")
        print(f"Negative samples: {self.stats['negative_samples']}")
        print(f"Internal sources: {self.stats['internal_sources']}")
        print(f"External sources: {self.stats['external_sources']}")
        print(f"Duplicates removed: {self.stats['duplicates_removed']}")
        print(f"Average importance: {self.stats['avg_importance']:.3f}")
        print(f"Average credibility: {self.stats['avg_credibility']:.3f}")

        print(f"\nTop categories:")
        for category, count in list(self.stats["categories"].items())[:5]:
            print(f"  {category}: {count}")

        print(f"\nTop sources:")
        for source, count in list(self.stats["sources"].items())[:5]:
            print(f"  {source}: {count}")

        print("=" * 60)


def setup_logging():
    """Setup logging for the dataset builder."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("logs/dataset_builder.log", mode="a")],
    )


def main():
    """Main function for baseline dataset building."""
    parser = argparse.ArgumentParser(description="Build baseline dataset for PulseAI Self-Tuning Predictor")
    parser.add_argument("--dry-run", action="store_true", help="Run without saving files")
    parser.add_argument("--config", type=str, help="Path to configuration file")

    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger("build_baseline_dataset")

    print("🧩 PulseAI Baseline Dataset Builder")
    print("=" * 60)

    try:
        builder = BaselineDatasetBuilder(args.config)
        result = builder.build_dataset(dry_run=args.dry_run)

        if result["success"]:
            print(f"\n✅ Dataset build completed successfully!")
            if not args.dry_run:
                print(f"📁 Dataset saved: {result['dataset_path']}")
                print(f"📊 Report saved: {result['report_path']}")
            else:
                print("🔍 Dry run completed - no files saved")
        else:
            print(f"\n❌ Dataset build failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error in dataset building: {e}")
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
