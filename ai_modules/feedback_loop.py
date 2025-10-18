"""
Feedback Loop — анализ корреляций между параметрами дайджеста и рейтингами.

Использует существующие данные: digests.feedback_score, digests.feedback_count.
Анализирует корреляции и автоматически корректирует параметры генерации.
"""

import logging
import json
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


class FeedbackAnalyzer:
    """Анализирует feedback пользователей и корректирует параметры генерации."""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def analyze_correlation(self, days: int = 7) -> Dict[str, Any]:
        """
        Вычисляет корреляции между параметрами дайджеста и пользовательскими оценками.

        Анализирует:
        - importance vs feedback_score
        - credibility vs feedback_score
        - style vs feedback_score
        - length vs feedback_score
        - generation_time vs feedback_score

        Args:
            days: Количество дней для анализа

        Returns:
            {
                "importance_correlation": 0.75,  # Pearson correlation
                "credibility_correlation": 0.82,
                "style_performance": {
                    "analytical": {"avg_score": 0.85, "count": 45},
                    "casual": {"avg_score": 0.72, "count": 30}
                },
                "optimal_length": 650,
                "recommendations": [
                    "Increase importance threshold to 0.65",
                    "Analytical style performs best"
                ],
                "sample_size": 120
            }
        """

        # Получаем дайджесты с рейтингами за последние N дней
        start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        try:
            digests = (
                self.supabase.table("digests")
                .select("*")
                .gte("created_at", start_date)
                .not_.is_("feedback_score", "null")
                .gte("feedback_count", 1)
                .execute()
            )

            if not digests.data or len(digests.data) < 10:
                logger.warning(f"Not enough feedback data: {len(digests.data) if digests.data else 0}")
                return {"error": "insufficient_data", "sample_size": len(digests.data) if digests.data else 0}

            # Извлекаем данные для анализа
            feedback_scores = []
            importance_vals = []
            credibility_vals = []
            styles = []
            lengths = []

            for digest in digests.data:
                feedback_scores.append(digest.get("feedback_score", 0))

                # Получаем параметры из meta JSONB
                meta = digest.get("meta", {})
                if isinstance(meta, str):
                    try:
                        meta = json.loads(meta)
                    except:
                        meta = {}

                importance_vals.append(meta.get("avg_importance", 0.5))
                credibility_vals.append(meta.get("avg_credibility", 0.5))
                styles.append(digest.get("style", "analytical"))

                # Длина текста
                content = digest.get("content", "") or digest.get("summary", "")
                word_count = len(content.split()) if content else 0
                lengths.append(word_count)

            # Вычисляем корреляции
            correlations = {}

            if len(feedback_scores) > 2:
                correlations["importance_correlation"] = self._pearson_correlation(importance_vals, feedback_scores)
                correlations["credibility_correlation"] = self._pearson_correlation(credibility_vals, feedback_scores)
                correlations["length_correlation"] = self._pearson_correlation(lengths, feedback_scores)

            # Анализ по стилям
            style_performance = {}
            for style in set(styles):
                style_scores = [score for score, s in zip(feedback_scores, styles) if s == style]
                if style_scores:
                    style_performance[style] = {
                        "avg_score": round(np.mean(style_scores), 3),
                        "count": len(style_scores),
                        "std": round(np.std(style_scores), 3),
                    }

            correlations["style_performance"] = style_performance

            # Оптимальная длина (находим диапазон с лучшими оценками)
            if lengths and feedback_scores:
                optimal_length = self._find_optimal_length(lengths, feedback_scores)
                correlations["optimal_length"] = optimal_length

            # Генерируем рекомендации
            recommendations = self._generate_recommendations(correlations)
            correlations["recommendations"] = recommendations
            correlations["sample_size"] = len(digests.data)

            logger.info(
                f"Feedback analysis completed: {len(digests.data)} samples, "
                f"importance_corr={correlations.get('importance_correlation', 0):.2f}"
            )

            return correlations

        except Exception as e:
            logger.error(f"Error analyzing feedback correlation: {e}")
            return {"error": "analysis_failed", "message": str(e)}

    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Вычисляет корреляцию Пирсона."""
        if len(x) < 3 or len(y) < 3:
            return 0.0
        try:
            corr, _ = stats.pearsonr(x, y)
            return round(corr, 3)
        except (ValueError, TypeError, RuntimeError):
            return 0.0

    def _find_optimal_length(self, lengths: List[int], scores: List[float]) -> int:
        """Находит оптимальную длину текста."""
        # Группируем по диапазонам длины
        ranges = [(0, 300), (300, 600), (600, 900), (900, 1500)]
        best_avg = 0
        best_length = 600

        for low, high in ranges:
            range_scores = [score for length, score in zip(lengths, scores) if low <= length < high]
            if range_scores and len(range_scores) >= 3:
                avg = np.mean(range_scores)
                if avg > best_avg:
                    best_avg = avg
                    best_length = (low + high) // 2

        return best_length

    def _generate_recommendations(self, correlations: Dict) -> List[str]:
        """Генерирует рекомендации на основе анализа."""
        recommendations = []

        # Корреляция с importance
        imp_corr = correlations.get("importance_correlation", 0)
        if imp_corr > 0.3:
            recommendations.append(
                f"Высокая корреляция с importance ({imp_corr:.2f}): " "увеличить порог фильтрации важных новостей"
            )
        elif imp_corr < -0.2:
            recommendations.append(
                f"Отрицательная корреляция с importance ({imp_corr:.2f}): " "пересмотреть критерии важности"
            )

        # Лучший стиль
        styles = correlations.get("style_performance", {})
        if styles:
            best_style = max(styles.items(), key=lambda x: x[1]["avg_score"])
            if best_style[1]["count"] >= 5:
                recommendations.append(
                    f"Стиль '{best_style[0]}' показывает лучшие результаты "
                    f"(avg: {best_style[1]['avg_score']:.2f}): использовать чаще"
                )

        # Оптимальная длина
        opt_length = correlations.get("optimal_length")
        if opt_length:
            recommendations.append(f"Оптимальная длина дайджеста: ~{opt_length} слов")

        return recommendations

    def adjust_weights(self, correlations: Dict) -> Dict[str, float]:
        """
        Автоматически корректирует веса на основе корреляций.

        Returns:
            {
                "importance_threshold": 0.65,
                "credibility_threshold": 0.75,
                "preferred_style": "analytical",
                "target_length": 650
            }
        """
        adjustments = {}

        # Корректируем importance threshold
        imp_corr = correlations.get("importance_correlation", 0)
        current_threshold = 0.6  # Default

        if imp_corr > 0.4:
            adjustments["importance_threshold"] = min(current_threshold + 0.05, 0.75)
        elif imp_corr < -0.2:
            adjustments["importance_threshold"] = max(current_threshold - 0.05, 0.4)
        else:
            adjustments["importance_threshold"] = current_threshold

        # Аналогично для credibility
        cred_corr = correlations.get("credibility_correlation", 0)
        current_cred = 0.7

        if cred_corr > 0.4:
            adjustments["credibility_threshold"] = min(current_cred + 0.05, 0.85)
        elif cred_corr < -0.2:
            adjustments["credibility_threshold"] = max(current_cred - 0.05, 0.5)
        else:
            adjustments["credibility_threshold"] = current_cred

        # Лучший стиль
        styles = correlations.get("style_performance", {})
        if styles:
            best_style = max(styles.items(), key=lambda x: x[1]["avg_score"])
            adjustments["preferred_style"] = best_style[0]

        # Целевая длина
        opt_length = correlations.get("optimal_length")
        if opt_length:
            adjustments["target_length"] = opt_length

        logger.info(f"Adjusted weights: {adjustments}")
        return adjustments

    def get_best_performing_digests(self, limit: int = 10) -> List[Dict]:
        """
        Получает топ дайджесты по feedback_score для обучения RAG.

        Args:
            limit: Количество лучших дайджестов

        Returns:
            Список дайджестов с высокими оценками
        """
        try:
            digests = (
                self.supabase.table("digests")
                .select("*")
                .not_.is_("feedback_score", "null")
                .gte("feedback_count", 2)
                .gte("feedback_score", 0.75)
                .order("feedback_score", desc=True)
                .limit(limit)
                .execute()
            )

            return digests.data or []

        except Exception as e:
            logger.error(f"Error getting best performing digests: {e}")
            return []


class FeedbackLoopManager:
    """Менеджер обратной связи - координирует анализ и обновления."""

    def __init__(self, supabase_client):
        self.analyzer = FeedbackAnalyzer(supabase_client)

    def run_feedback_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Запускает полный анализ обратной связи."""
        logger.info(f"Starting feedback analysis for last {days} days")

        # Анализируем корреляции
        correlations = self.analyzer.analyze_correlation(days)

        if "error" in correlations:
            logger.warning(f"Feedback analysis failed: {correlations}")
            return correlations

        # Корректируем веса
        adjustments = self.analyzer.adjust_weights(correlations)

        # Получаем лучшие дайджесты для RAG
        best_digests = self.analyzer.get_best_performing_digests(limit=20)

        result = {
            "correlations": correlations,
            "adjustments": adjustments,
            "best_digests_count": len(best_digests),
            "analysis_date": datetime.now(timezone.utc).isoformat(),
            "status": "success",
        }

        logger.info("Feedback analysis completed successfully")
        return result
