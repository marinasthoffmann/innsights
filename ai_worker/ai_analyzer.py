import torch
from transformers import pipeline
from loguru import logger

class SentimentAnalyzer:
    """Sentiment analyzer using BERT"""

    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        logger.info(f"🔧 Using device: {'GPU' if self.device == 0 else 'CPU'}")
        
        logger.info("📥 Loading sentiment model...")
        self.analyzer = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment",
            device=self.device
        )
        logger.info("✅ Model loaded!")

    def analyze(self, text: str, rating: int) -> dict:
        """Analyze sentiment"""
        try:
            text_truncated = text[:512]
            
            result = self.analyzer(text_truncated)[0]
            
            label_to_score = {
                "1 star": -1.0,
                "2 stars": -0.5,
                "3 stars": 0.0,
                "4 stars": 0.5,
                "5 stars": 1.0
            }
            
            model_score = label_to_score.get(result['label'], 0.0)
            rating_score = (rating - 3) / 2
            final_score = (model_score * 0.6) + (rating_score * 0.4)

            if final_score > 0.3:
                label = "positive"
            elif final_score < -0.3:
                label = "negative"
            else:
                label = "neutral"
            
            return {
                'sentiment_score': round(final_score, 3),
                'sentiment_label': label
            }
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            rating_score = (rating - 3) / 2
            label = "positive" if rating >= 4 else "negative" if rating <= 2 else "neutral"
            return {'sentiment_score': round(rating_score, 3), 'sentiment_label': label}
        
# Global instance
_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer
