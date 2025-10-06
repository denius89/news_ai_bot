"""
Self-Tuning Model Trainer for Local Predictor.

This module trains and manages the local predictor model using
collected training data.
"""

import json
import logging
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

import yaml

from ai_modules.metrics import get_metrics

logger = logging.getLogger("self_tuning_trainer")


class SelfTuningTrainer:
    """
    Trains and manages the local predictor model.
    
    Uses scikit-learn to train models for importance and credibility
    prediction based on collected training data.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize model trainer with configuration."""
        self.config = self._load_config(config_path)
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        # Model paths
        self.importance_model_path = self.models_dir / "local_predictor_importance.pkl"
        self.credibility_model_path = self.models_dir / "local_predictor_credibility.pkl"
        self.metadata_path = self.models_dir / "local_predictor_meta.json"
        
        # Configuration
        self.model_type = self.config.get('self_tuning', {}).get('model_type', 'logreg')
        self.replace_threshold = self.config.get('self_tuning', {}).get('replace_threshold', 0.01)
        self.backup_enabled = self.config.get('self_tuning', {}).get('backup_enabled', True)
        
        # Metrics
        self.metrics = get_metrics()
        
        # Model instances
        self.importance_model = None
        self.credibility_model = None
        self.scaler = StandardScaler()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "ai_optimization.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _create_model(self, model_type: str):
        """
        Create model instance based on type.
        
        Args:
            model_type: Type of model to create
            
        Returns:
            Model instance
        """
        if model_type == "logreg":
            return LogisticRegression(random_state=42, max_iter=1000)
        elif model_type == "randomforest":
            return RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        else:
            logger.warning(f"Unknown model type {model_type}, using LogisticRegression")
            return LogisticRegression(random_state=42, max_iter=1000)
    
    def _load_dataset(self, dataset_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load and prepare dataset for training.
        
        Args:
            dataset_path: Path to dataset CSV file
            
        Returns:
            Tuple of (features_df, labels_df)
        """
        try:
            df = pd.read_csv(dataset_path)
            
            # Separate features and labels
            feature_columns = [col for col in df.columns if col not in [
                'importance_label', 'credibility_label', 'importance_score', 'credibility_score',
                'source', 'category', 'title', 'timestamp'
            ]]
            
            features_df = df[feature_columns].fillna(0)
            labels_df = df[['importance_label', 'credibility_label']]
            
            logger.info(f"Loaded dataset: {len(df)} examples, {len(feature_columns)} features")
            
            return features_df, labels_df
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise
    
    def _evaluate_model(self, model, X_test: pd.DataFrame, y_test: pd.Series, 
                       task_name: str) -> Dict[str, float]:
        """
        Evaluate model performance.
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            task_name: Name of the task (for logging)
            
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            # Make predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
            
            # Calculate metrics
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            metrics = {
                'f1_score': f1,
                'accuracy': (y_pred == y_test).mean()
            }
            
            # Add AUC if probabilities available
            if y_pred_proba is not None:
                try:
                    auc = roc_auc_score(y_test, y_pred_proba)
                    metrics['auc'] = auc
                except Exception:
                    metrics['auc'] = 0.0
            
            # Cross-validation score
            try:
                cv_scores = cross_val_score(model, X_test, y_test, cv=3, scoring='f1_weighted')
                metrics['cv_f1_mean'] = cv_scores.mean()
                metrics['cv_f1_std'] = cv_scores.std()
            except Exception:
                metrics['cv_f1_mean'] = f1
                metrics['cv_f1_std'] = 0.0
            
            logger.info(f"{task_name} model evaluation: F1={f1:.3f}, AUC={metrics.get('auc', 0.0):.3f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error evaluating {task_name} model: {e}")
            return {'f1_score': 0.0, 'accuracy': 0.0, 'auc': 0.0}
    
    def _create_backup(self, model_path: Path) -> Optional[Path]:
        """
        Create backup of existing model.
        
        Args:
            model_path: Path to model file
            
        Returns:
            Path to backup file or None
        """
        if not self.backup_enabled or not model_path.exists():
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = model_path.parent / f"{model_path.stem}_backup_{timestamp}.pkl"
            
            import shutil
            shutil.copy2(model_path, backup_path)
            logger.info(f"Model backup created: {backup_path}")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating model backup: {e}")
            return None
    
    def _load_existing_metadata(self) -> Dict[str, Any]:
        """
        Load existing model metadata.
        
        Returns:
            Dictionary with existing metadata
        """
        if not self.metadata_path.exists():
            return {}
        
        try:
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading metadata: {e}")
            return {}
    
    def _save_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Save model metadata.
        
        Args:
            metadata: Metadata to save
        """
        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            logger.info(f"Model metadata saved: {self.metadata_path}")
            
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def train_models(self, dataset_path: Path) -> Dict[str, Any]:
        """
        Train importance and credibility models.
        
        Args:
            dataset_path: Path to training dataset
            
        Returns:
            Dictionary with training results
        """
        logger.info("Starting model training...")
        
        try:
            # Load dataset
            features_df, labels_df = self._load_dataset(dataset_path)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features_df, labels_df, test_size=0.2, random_state=42, stratify=labels_df['importance_label']
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            results = {
                'success': True,
                'dataset_size': len(features_df),
                'train_size': len(X_train),
                'test_size': len(X_test),
                'features_count': len(features_df.columns),
                'models_trained': [],
                'improvements': {}
            }
            
            # Train importance model
            importance_result = self._train_importance_model(
                X_train_scaled, X_test_scaled, 
                y_train['importance_label'], y_test['importance_label']
            )
            results['models_trained'].append('importance')
            results['improvements']['importance'] = importance_result
            
            # Train credibility model
            credibility_result = self._train_credibility_model(
                X_train_scaled, X_test_scaled,
                y_train['credibility_label'], y_test['credibility_label']
            )
            results['models_trained'].append('credibility')
            results['improvements']['credibility'] = credibility_result
            
            # Save metadata
            metadata = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'dataset_size': len(features_df),
                'model_type': self.model_type,
                'features': list(features_df.columns),
                'importance_model': importance_result,
                'credibility_model': credibility_result,
                'version': self._get_next_version()
            }
            self._save_metadata(metadata)
            
            # Update metrics
            self.metrics.increment_self_tuning_runs()
            self.metrics.increment_self_tuning_models_trained(2)  # Two models trained
            
            total_improvements = sum(
                result.get('improvement', 0) for result in results['improvements'].values()
            )
            if total_improvements > 0:
                self.metrics.increment_self_tuning_models_replaced()
            
            logger.info(f"Model training completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in model training: {e}")
            return {
                'success': False,
                'error': str(e),
                'dataset_size': 0,
                'models_trained': []
            }
    
    def _train_importance_model(self, X_train: np.ndarray, X_test: np.ndarray,
                               y_train: pd.Series, y_test: pd.Series) -> Dict[str, Any]:
        """
        Train importance prediction model.
        
        Args:
            X_train: Training features
            X_test: Test features
            y_train: Training labels
            y_test: Test labels
            
        Returns:
            Dictionary with training results
        """
        logger.info("Training importance model...")
        
        # Load existing model for comparison
        existing_metrics = self._get_existing_model_metrics('importance')
        
        # Create and train new model
        model = self._create_model(self.model_type)
        model.fit(X_train, y_train)
        
        # Evaluate new model
        new_metrics = self._evaluate_model(model, X_test, y_test, "Importance")
        
        # Check if improvement is significant
        improvement = 0.0
        should_replace = False
        
        if existing_metrics:
            improvement = new_metrics['f1_score'] - existing_metrics.get('f1_score', 0.0)
            should_replace = improvement >= self.replace_threshold
            logger.info(f"Importance model improvement: {improvement:.3f} (threshold: {self.replace_threshold})")
        else:
            should_replace = True  # No existing model
            logger.info("No existing importance model found, using new model")
        
        if should_replace:
            # Create backup
            self._create_backup(self.importance_model_path)
            
            # Save new model
            self._save_model(model, self.importance_model_path)
            self.importance_model = model
            
            logger.info(f"[SELF-TUNING] Importance model replaced (F1: {new_metrics['f1_score']:.3f})")
        else:
            logger.info(f"[SELF-TUNING] Importance model not replaced (improvement too small)")
        
        return {
            'f1_score': new_metrics['f1_score'],
            'improvement': improvement,
            'replaced': should_replace,
            'model_type': self.model_type
        }
    
    def _train_credibility_model(self, X_train: np.ndarray, X_test: np.ndarray,
                                y_train: pd.Series, y_test: pd.Series) -> Dict[str, Any]:
        """
        Train credibility prediction model.
        
        Args:
            X_train: Training features
            X_test: Test features
            y_train: Training labels
            y_test: Test labels
            
        Returns:
            Dictionary with training results
        """
        logger.info("Training credibility model...")
        
        # Load existing model for comparison
        existing_metrics = self._get_existing_model_metrics('credibility')
        
        # Create and train new model
        model = self._create_model(self.model_type)
        model.fit(X_train, y_train)
        
        # Evaluate new model
        new_metrics = self._evaluate_model(model, X_test, y_test, "Credibility")
        
        # Check if improvement is significant
        improvement = 0.0
        should_replace = False
        
        if existing_metrics:
            improvement = new_metrics['f1_score'] - existing_metrics.get('f1_score', 0.0)
            should_replace = improvement >= self.replace_threshold
            logger.info(f"Credibility model improvement: {improvement:.3f} (threshold: {self.replace_threshold})")
        else:
            should_replace = True  # No existing model
            logger.info("No existing credibility model found, using new model")
        
        if should_replace:
            # Create backup
            self._create_backup(self.credibility_model_path)
            
            # Save new model
            self._save_model(model, self.credibility_model_path)
            self.credibility_model = model
            
            logger.info(f"[SELF-TUNING] Credibility model replaced (F1: {new_metrics['f1_score']:.3f})")
        else:
            logger.info(f"[SELF-TUNING] Credibility model not replaced (improvement too small)")
        
        return {
            'f1_score': new_metrics['f1_score'],
            'improvement': improvement,
            'replaced': should_replace,
            'model_type': self.model_type
        }
    
    def _get_existing_model_metrics(self, model_type: str) -> Optional[Dict[str, float]]:
        """
        Get metrics from existing model metadata.
        
        Args:
            model_type: Type of model ('importance' or 'credibility')
            
        Returns:
            Dictionary with existing metrics or None
        """
        metadata = self._load_existing_metadata()
        return metadata.get(f'{model_type}_model', {}).get('metrics')
    
    def _save_model(self, model, model_path: Path) -> None:
        """
        Save trained model to file.
        
        Args:
            model: Trained model
            model_path: Path to save model
        """
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            logger.info(f"Model saved: {model_path}")
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def _get_next_version(self) -> int:
        """
        Get next version number for model.
        
        Returns:
            Next version number
        """
        metadata = self._load_existing_metadata()
        current_version = metadata.get('version', 0)
        return current_version + 1
    
    def load_models(self) -> bool:
        """
        Load existing trained models.
        
        Returns:
            True if models loaded successfully, False otherwise
        """
        try:
            # Load importance model
            if self.importance_model_path.exists():
                with open(self.importance_model_path, 'rb') as f:
                    self.importance_model = pickle.load(f)
                logger.info("Importance model loaded successfully")
            else:
                logger.warning("Importance model not found")
            
            # Load credibility model
            if self.credibility_model_path.exists():
                with open(self.credibility_model_path, 'rb') as f:
                    self.credibility_model = pickle.load(f)
                logger.info("Credibility model loaded successfully")
            else:
                logger.warning("Credibility model not found")
            
            # Load scaler
            scaler_path = self.models_dir / "scaler.pkl"
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("Feature scaler loaded successfully")
            
            return self.importance_model is not None and self.credibility_model is not None
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False
    
    def predict(self, features: Dict[str, float]) -> Tuple[float, float]:
        """
        Make predictions using loaded models.
        
        Args:
            features: Dictionary with feature values
            
        Returns:
            Tuple of (importance_score, credibility_score)
        """
        try:
            if not self.importance_model or not self.credibility_model:
                logger.warning("Models not loaded, using fallback predictions")
                return 0.5, 0.5
            
            # Convert features to array
            # This assumes features are in the same order as training
            feature_values = list(features.values())
            feature_array = np.array(feature_values).reshape(1, -1)
            
            # Scale features
            feature_array_scaled = self.scaler.transform(feature_array)
            
            # Make predictions
            importance_score = self.importance_model.predict_proba(feature_array_scaled)[0][1]
            credibility_score = self.credibility_model.predict_proba(feature_array_scaled)[0][1]
            
            return float(importance_score), float(credibility_score)
            
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            return 0.5, 0.5
    
    def is_enabled(self) -> bool:
        """Check if self-tuning is enabled."""
        return self.config.get('features', {}).get('self_tuning_enabled', True)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about current models.
        
        Returns:
            Dictionary with model information
        """
        metadata = self._load_existing_metadata()
        
        return {
            'importance_model_loaded': self.importance_model is not None,
            'credibility_model_loaded': self.credibility_model is not None,
            'model_type': self.model_type,
            'last_training': metadata.get('timestamp'),
            'version': metadata.get('version', 0),
            'dataset_size': metadata.get('dataset_size', 0)
        }


# Global trainer instance
_trainer_instance: Optional[SelfTuningTrainer] = None


def get_self_tuning_trainer() -> SelfTuningTrainer:
    """Get global self-tuning trainer instance."""
    global _trainer_instance
    if _trainer_instance is None:
        _trainer_instance = SelfTuningTrainer()
    return _trainer_instance


def train_models(dataset_path: Path) -> Dict[str, Any]:
    """
    Convenience function to train models.
    
    Args:
        dataset_path: Path to training dataset
        
    Returns:
        Dictionary with training results
    """
    trainer = get_self_tuning_trainer()
    if not trainer.is_enabled():
        logger.info("Self-tuning is disabled, skipping model training")
        return {'success': False, 'error': 'Self-tuning disabled'}
    
    return trainer.train_models(dataset_path)
