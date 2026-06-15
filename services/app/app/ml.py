import math
import re
from collections import Counter
from typing import Dict, Any, List, Tuple


TRAINING_DATA: List[Tuple[str, str]] = [
    ("employee asks about leave policy and manager approval", "HR"),
    ("candidate interview feedback and hiring process", "HR"),
    ("benefits payroll annual leave remote work policy", "HR"),
    ("invoice payment revenue report budget approval", "Finance"),
    ("quarterly finance report confidential forecast", "Finance"),
    ("purchase order vendor tax accounting", "Finance"),
    ("vpn mfa password reset laptop endpoint encryption", "Security"),
    ("phishing alert access control suspicious login", "Security"),
    ("data classification confidential document policy", "Security"),
    ("server outage application latency database error", "IT"),
    ("api failure deployment rollback monitoring alert", "IT"),
    ("user cannot connect to system ticket incident", "IT"),
]


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


class TinyMLClassifier:
    """
    Pure-Python multinomial Naive Bayes classifier.

    This keeps the demo fully open-source and avoids compiled ML libraries,
    which makes offline setup simpler across Windows, macOS, and Linux.
    """

    def __init__(self):
        self.labels = sorted(set(label for _, label in TRAINING_DATA))
        self.label_doc_counts = Counter()
        self.label_token_counts: Dict[str, Counter] = {label: Counter() for label in self.labels}
        self.label_total_tokens: Dict[str, int] = {label: 0 for label in self.labels}
        self.vocabulary = set()

        for text, label in TRAINING_DATA:
            tokens = tokenize(text)
            self.label_doc_counts[label] += 1
            self.label_token_counts[label].update(tokens)
            self.label_total_tokens[label] += len(tokens)
            self.vocabulary.update(tokens)

        self.total_docs = len(TRAINING_DATA)

    def classify(self, text: str) -> Dict[str, Any]:
        tokens = tokenize(text)
        vocab_size = max(len(self.vocabulary), 1)

        log_scores = {}
        for label in self.labels:
            prior = self.label_doc_counts[label] / self.total_docs
            log_prob = math.log(prior)

            total_tokens = self.label_total_tokens[label]
            token_counts = self.label_token_counts[label]

            for token in tokens:
                count = token_counts.get(token, 0)
                prob = (count + 1) / (total_tokens + vocab_size)
                log_prob += math.log(prob)

            log_scores[label] = log_prob

        max_log = max(log_scores.values())
        exp_scores = {label: math.exp(score - max_log) for label, score in log_scores.items()}
        total = sum(exp_scores.values()) or 1.0
        probabilities = {label: exp_scores[label] / total for label in self.labels}

        label = max(probabilities.items(), key=lambda x: x[1])[0]
        scores = {
            cls: round(float(prob), 4)
            for cls, prob in sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        }

        return {
            "label": label,
            "scores": scores,
            "model_source": "approved-local-training-data",
            "model_type": "pure-python-naive-bayes",
            "runtime": "offline-local",
        }
