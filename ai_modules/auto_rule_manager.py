"""
Auto Rule Manager for Auto-Learning Filter.

This module manages automatic updates to prefilter rules based on
rejection analysis results.
"""

import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from ai_modules.metrics import get_metrics

logger = logging.getLogger("auto_rule_manager")


class AutoRuleManager:
    """
    Manages automatic updates to prefilter rules.

    Processes analysis results from RejectionAnalyzer and updates
    prefilter_rules.yaml with new rules and adjustments.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize auto rule manager with configuration."""
        self.config = self._load_config(config_path)
        self.rules_path = Path("config/prefilter_rules.yaml")
        self.backup_enabled = self.config.get("features", {}).get("auto_learn_backup_enabled", True)
        self.auto_apply = self.config.get("features", {}).get("auto_learn_enabled", True)

        # Metrics
        self.metrics = get_metrics()

        # Track changes
        self.changes_made = {"rules_added": 0, "rules_removed": 0, "backups_created": 0}

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "prefilter_rules.yaml"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def _create_backup(self) -> Optional[Path]:
        """Create backup of current rules file."""
        if not self.backup_enabled:
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.rules_path.parent / f"prefilter_rules_backup_{timestamp}.yaml"

            shutil.copy2(self.rules_path, backup_path)
            logger.info(f"Backup created: {backup_path}")

            self.changes_made["backups_created"] += 1
            return backup_path

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None

    def _load_rules(self) -> Dict:
        """Load current prefilter rules."""
        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
            return {}

    def _save_rules(self, rules: Dict) -> bool:
        """Save updated rules to file."""
        try:
            with open(self.rules_path, "w", encoding="utf-8") as f:
                yaml.dump(rules, f, default_flow_style=False, allow_unicode=True, indent=2)

            logger.info(f"Rules updated: {self.rules_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving rules: {e}")
            return False

    def _update_metadata(self, rules: Dict, changes: Dict) -> None:
        """Update auto-learning metadata in rules."""
        if "auto_learn_metadata" not in rules:
            rules["auto_learn_metadata"] = {}

        metadata = rules["auto_learn_metadata"]
        metadata["last_analysis"] = datetime.now(timezone.utc).isoformat()
        metadata["total_runs"] = metadata.get("total_runs", 0) + 1
        metadata["rules_added"] = metadata.get("rules_added", 0) + changes.get("rules_added", 0)
        metadata["rules_removed"] = metadata.get(
            "rules_removed", 0) + changes.get("rules_removed", 0)
        metadata["last_backup"] = datetime.now(timezone.utc).isoformat()

    def _add_stop_markers(self, rules: Dict, recommendations: List[Dict]) -> int:
        """Add new stop markers based on recommendations."""
        added_count = 0

        # Initialize auto_generated section if needed
        if "auto_generated" not in rules:
            rules["auto_generated"] = {}
        if "stop_markers" not in rules["auto_generated"]:
            rules["auto_generated"]["stop_markers"] = []

        current_stop_markers = set(rules.get("stop_markers", []))
        auto_stop_markers = set(rules["auto_generated"]["stop_markers"])
        all_stop_markers = current_stop_markers | auto_stop_markers

        for rec in recommendations:
            word = rec["word"]
            confidence = rec["confidence"]

            # Only add if not already present and confidence is high enough
            if word not in all_stop_markers and confidence >= 0.5:
                rules["auto_generated"]["stop_markers"].append(
                    {
                        "word": word,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "confidence": confidence,
                        "samples_count": rec["count"],
                        "auto": True,
                    }
                )
                added_count += 1
                logger.info(
                    f"[AUTOLEARN] Added stop marker: '{word}' (confidence: {confidence:.2f})")

        return added_count

    def _add_source_blacklist(self, rules: Dict, recommendations: List[Dict]) -> int:
        """Add sources to blacklist based on recommendations."""
        added_count = 0

        # Initialize source blacklist if needed
        if "auto_generated" not in rules:
            rules["auto_generated"] = {}
        if "source_blacklist" not in rules["auto_generated"]:
            rules["auto_generated"]["source_blacklist"] = []

        current_blacklist = set()
        for item in rules["auto_generated"]["source_blacklist"]:
            if isinstance(item, dict):
                current_blacklist.add(item["source"])
            else:
                current_blacklist.add(item)

        for rec in recommendations:
            source = rec["source"]
            confidence = rec["confidence"]

            # Only add if not already blacklisted and confidence is high enough
            if source not in current_blacklist and confidence >= 0.7:
                rules["auto_generated"]["source_blacklist"].append(
                    {
                        "source": source,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "confidence": confidence,
                        "samples_count": rec["count"],
                        "auto": True,
                    }
                )
                added_count += 1
                logger.info(
                    f"[AUTOLEARN] Added to source blacklist: '{source}' (confidence: {confidence:.2f})")

        return added_count

    def _cleanup_old_rules(self, rules: Dict) -> int:
        """Remove old auto-generated rules that haven't been reinforced."""
        removed_count = 0

        if "auto_generated" not in rules:
            return removed_count

        cutoff_date = datetime.now(timezone.utc).replace(
            day=1)  # Remove rules older than current month

        # Clean up old stop markers
        if "stop_markers" in rules["auto_generated"]:
            original_count = len(rules["auto_generated"]["stop_markers"])
            rules["auto_generated"]["stop_markers"] = [rule for rule in rules["auto_generated"][
                "stop_markers"] if self._should_keep_rule(rule, cutoff_date)]
            removed_count += original_count - len(rules["auto_generated"]["stop_markers"])

        # Clean up old source blacklist entries
        if "source_blacklist" in rules["auto_generated"]:
            original_count = len(rules["auto_generated"]["source_blacklist"])
            rules["auto_generated"]["source_blacklist"] = [
                rule
                for rule in rules["auto_generated"]["source_blacklist"]
                if self._should_keep_rule(rule, cutoff_date)
            ]
            removed_count += original_count - len(rules["auto_generated"]["source_blacklist"])

        return removed_count

    def _should_keep_rule(self, rule: Dict, cutoff_date: datetime) -> bool:
        """Determine if a rule should be kept based on age and usage."""
        try:
            if not isinstance(rule, dict):
                return True  # Keep non-dict rules (backward compatibility)

            created_at_str = rule.get("created_at")
            if not created_at_str:
                return True  # Keep rules without creation date

            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))

            # Keep rules created after cutoff date
            if created_at >= cutoff_date:
                return True

            # Keep high-confidence rules even if old
            confidence = rule.get("confidence", 0)
            if confidence >= 0.8:
                return True

            # Remove old, low-confidence rules
            logger.debug(f"Removing old rule: {rule}")
            return False

        except Exception as e:
            logger.warning(f"Error evaluating rule age: {e}")
            return True  # Keep rule if evaluation fails

    def apply_recommendations(self, analysis: Dict) -> Dict:
        """
        Apply recommendations from analysis to rules.

        Args:
            analysis: Analysis results from RejectionAnalyzer

        Returns:
            Dictionary with applied changes summary
        """
        if not self.auto_apply:
            logger.info("Auto-learning is disabled, only generating recommendations")
            return self._generate_recommendations_only(analysis)

        logger.info("Applying auto-learning recommendations...")

        # Create backup before making changes
        backup_path = self._create_backup()

        # Load current rules
        rules = self._load_rules()
        if not rules:
            logger.error("Failed to load rules, aborting auto-learning")
            return {"error": "Failed to load rules"}

        # Reset change tracking
        self.changes_made = {
            "rules_added": 0,
            "rules_removed": 0,
            "backups_created": 1 if backup_path else 0}

        try:
            recommendations = analysis.get("recommendations", {})

            # Add stop markers
            stop_marker_recs = recommendations.get("add_stop_markers", [])
            added_stop_markers = self._add_stop_markers(rules, stop_marker_recs)
            self.changes_made["rules_added"] += added_stop_markers

            # Add source blacklist entries
            blacklist_recs = recommendations.get("source_blacklist", [])
            added_blacklist = self._add_source_blacklist(rules, blacklist_recs)
            self.changes_made["rules_added"] += added_blacklist

            # Cleanup old rules
            removed_rules = self._cleanup_old_rules(rules)
            self.changes_made["rules_removed"] += removed_rules

            # Update metadata
            self._update_metadata(rules, self.changes_made)

            # Save updated rules
            if self._save_rules(rules):
                # Update metrics
                self.metrics.increment_auto_learn_runs()
                self.metrics.increment_auto_rules_added(added_stop_markers + added_blacklist)
                self.metrics.increment_auto_rules_removed(removed_rules)

                logger.info(
                    f"[AUTOLEARN] Applied changes: {added_stop_markers} stop markers, "
                    f"{added_blacklist} blacklist entries, {removed_rules} rules removed"
                )

                return {
                    "success": True,
                    "changes": self.changes_made,
                    "backup_path": str(backup_path) if backup_path else None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            else:
                logger.error("Failed to save updated rules")
                return {"error": "Failed to save rules"}

        except Exception as e:
            logger.error(f"Error applying recommendations: {e}")
            return {"error": str(e)}

    def _generate_recommendations_only(self, analysis: Dict) -> Dict:
        """Generate recommendations without applying them."""
        recommendations = analysis.get("recommendations", {})

        stop_marker_count = len(recommendations.get("add_stop_markers", []))
        blacklist_count = len(recommendations.get("source_blacklist", []))

        logger.info(
            f"[AUTOLEARN] Recommendations (not applied): "
            f"{stop_marker_count} stop markers, {blacklist_count} blacklist entries"
        )

        return {
            "success": True,
            "mode": "recommendations_only",
            "recommendations": {
                "stop_markers": stop_marker_count,
                "blacklist_entries": blacklist_count,
                "rule_adjustments": len(recommendations.get("rule_adjustments", [])),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_active_auto_rules_count(self) -> int:
        """Get count of active auto-generated rules."""
        try:
            rules = self._load_rules()
            if "auto_generated" not in rules:
                return 0

            auto_rules = rules["auto_generated"]
            count = 0

            # Count stop markers
            if "stop_markers" in auto_rules:
                count += len(auto_rules["stop_markers"])

            # Count blacklist entries
            if "source_blacklist" in auto_rules:
                count += len(auto_rules["source_blacklist"])

            return count

        except Exception as e:
            logger.error(f"Error counting auto rules: {e}")
            return 0

    def is_enabled(self) -> bool:
        """Check if auto-learning is enabled."""
        return self.config.get("features", {}).get("auto_learn_enabled", True)


# Global rule manager instance
_rule_manager_instance: Optional[AutoRuleManager] = None


def get_auto_rule_manager() -> AutoRuleManager:
    """Get global auto rule manager instance."""
    global _rule_manager_instance
    if _rule_manager_instance is None:
        _rule_manager_instance = AutoRuleManager()
    return _rule_manager_instance


def apply_auto_learning(analysis: Dict) -> Dict:
    """
    Convenience function to apply auto-learning recommendations.

    Args:
        analysis: Analysis results from RejectionAnalyzer

    Returns:
        Dictionary with applied changes summary
    """
    rule_manager = get_auto_rule_manager()
    if not rule_manager.is_enabled():
        logger.info("Auto-learning is disabled, skipping rule updates")
        return {"success": True, "mode": "disabled"}

    return rule_manager.apply_recommendations(analysis)
