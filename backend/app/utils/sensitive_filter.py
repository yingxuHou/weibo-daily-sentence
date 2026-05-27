"""Sensitive word filter"""
import re
from typing import List, Set


class SensitiveWordFilter:
    def __init__(self, words: List[str] = None):
        """初始化敏感词过滤器"""
        self.sensitive_words: Set[str] = set(words) if words else set()
        self._build_pattern()

    def _build_pattern(self):
        """构建正则表达式模式"""
        if self.sensitive_words:
            escaped_words = [re.escape(word) for word in self.sensitive_words]
            self.pattern = re.compile('|'.join(escaped_words), re.IGNORECASE)
        else:
            self.pattern = None

    def add_words(self, words: List[str]):
        """添加敏感词"""
        self.sensitive_words.update(words)
        self._build_pattern()

    def remove_words(self, words: List[str]):
        """移除敏感词"""
        self.sensitive_words.difference_update(words)
        self._build_pattern()

    def contains_sensitive_word(self, text: str) -> bool:
        """检查文本是否包含敏感词"""
        if not self.pattern:
            return False
        return bool(self.pattern.search(text))

    def find_sensitive_words(self, text: str) -> List[str]:
        """查找文本中的所有敏感词"""
        if not self.pattern:
            return []
        matches = self.pattern.findall(text)
        return list(set(matches))

    def filter_text(self, text: str, replacement: str = "***") -> str:
        """过滤文本中的敏感词"""
        if not self.pattern:
            return text
        return self.pattern.sub(replacement, text)


default_sensitive_words = [
    "政治",
    "暴力",
    "色情",
]

sensitive_filter = SensitiveWordFilter(default_sensitive_words)
