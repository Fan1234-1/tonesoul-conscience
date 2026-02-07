"""
ToneSoul Conscience Layer - Benevolence Filter
仁慈函數：確保 AI 輸出誠實且負責任

CPT 語場整合：
- C (Context): 上下文環境評估
- P (Phrase): 語句結構分析
- T (Tension): 語義張力計算
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set
from enum import Enum
import re


class AuditLayer(Enum):
    """語義層級"""
    L1 = "operational"    # 操作事實層
    L2 = "semantic"       # 語義模型層
    L3 = "metaphor"       # 抽象隱喻層


class AuditResult(Enum):
    """審計結果"""
    PASS = "pass"
    FLAG = "flag"
    REJECT = "reject"
    INTERCEPT = "intercept"


@dataclass
class BenevolenceAudit:
    """
    仁慈函數審計結果
    
    三層審計機制：
    1. 屬性歸屬檢查 (Attribute Attribution)
    2. 影子路徑追蹤 (Shadow Tracking)
    3. 仁慈函數判定 (Benevolence Filter)
    """
    
    # 審計結果
    attribute_check: AuditResult = AuditResult.PASS
    shadow_check: AuditResult = AuditResult.PASS
    benevolence_check: AuditResult = AuditResult.PASS
    
    # 最終判定
    final_result: AuditResult = AuditResult.PASS
    error_log: Optional[str] = None
    
    # CPT 語場分數
    context_score: float = 0.0
    phrase_score: float = 0.0
    tension_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "attribute_check": self.attribute_check.value,
            "shadow_check": self.shadow_check.value,
            "benevolence_check": self.benevolence_check.value,
            "final_result": self.final_result.value,
            "error_log": self.error_log,
            "cpt_scores": {
                "context": round(self.context_score, 3),
                "phrase": round(self.phrase_score, 3),
                "tension": round(self.tension_score, 3),
            }
        }


class BenevolenceFilter:
    """
    仁慈函數過濾器
    
    核心原則：
    - γ·Honesty > β·Helpfulness
    - 誠實優先於討好
    """
    
    # 討好詞彙（可能是為了取悅用戶而不是誠實）
    PLEASING_PATTERNS = [
        r"absolutely",
        r"definitely",
        r"of course",
        r"certainly",
        r"no problem",
        r"sure thing",
        r"I'd be happy to",
        r"Great question",
    ]
    
    # 不確定詞彙（誠實的標誌）
    HONEST_PATTERNS = [
        r"I'm not sure",
        r"I don't know",
        r"might be",
        r"could be",
        r"uncertain",
        r"approximately",
        r"based on limited",
    ]
    
    def __init__(self, user_protocol: str = "γ·Honesty > β·Helpfulness"):
        self.user_protocol = user_protocol
        self.honesty_priority = "Honesty" in user_protocol.split(">")[0]
    
    def audit(
        self,
        proposed_action: str,
        context_fragments: List[str],
        action_basis: str = "Inference",
        current_layer: AuditLayer = AuditLayer.L2,
    ) -> BenevolenceAudit:
        """
        執行三層審計
        
        Args:
            proposed_action: 提議的輸出
            context_fragments: 上下文碎片（記憶/檢索結果）
            action_basis: 行動依據類型
            current_layer: 當前語義層級
        
        Returns:
            BenevolenceAudit: 審計結果
        """
        audit = BenevolenceAudit()
        
        # 1. 屬性歸屬檢查
        audit.attribute_check = self._check_attribute(
            action_basis, current_layer
        )
        
        # 2. 影子路徑追蹤
        audit.shadow_check, audit.context_score = self._check_shadow(
            proposed_action, context_fragments
        )
        
        # 3. 仁慈函數判定
        audit.benevolence_check, audit.phrase_score = self._check_benevolence(
            proposed_action
        )
        
        # 計算張力分數
        audit.tension_score = self._calculate_tension(
            audit.context_score,
            audit.phrase_score,
        )
        
        # 最終判定
        audit.final_result, audit.error_log = self._finalize(audit)
        
        return audit
    
    def _check_attribute(
        self,
        action_basis: str,
        current_layer: AuditLayer,
    ) -> AuditResult:
        """
        屬性歸屬檢查
        
        規則：
        IF action_basis == 'Inference' AND layer != 'L2'
        THEN FLAG_ERROR('跨層混用')
        """
        if action_basis == "Inference" and current_layer != AuditLayer.L2:
            return AuditResult.FLAG
        return AuditResult.PASS
    
    def _check_shadow(
        self,
        proposed_action: str,
        context_fragments: List[str],
    ) -> tuple[AuditResult, float]:
        """
        影子路徑追蹤
        
        規則：
        IF proposed_action NOT IN context_fragments
        THEN REJECT('無影子的輸出')
        """
        if not context_fragments:
            return AuditResult.PASS, 0.5  # 沒有上下文，給中間分數
        
        # 計算上下文覆蓋率
        action_words = set(proposed_action.lower().split())
        context_words: Set[str] = set()
        for fragment in context_fragments:
            context_words.update(fragment.lower().split())
        
        if not action_words:
            return AuditResult.PASS, 0.0
        
        overlap = len(action_words & context_words) / len(action_words)
        
        # 覆蓋率低於 30% 視為「無影子」
        if overlap < 0.3:
            return AuditResult.REJECT, overlap
        
        return AuditResult.PASS, overlap
    
    def _check_benevolence(
        self,
        proposed_action: str,
    ) -> tuple[AuditResult, float]:
        """
        仁慈函數判定
        
        規則：
        IF is_pleasing_user AND is_factually_incorrect (no honest markers)
        THEN INTERCEPT('攔截無效敘事')
        """
        text = proposed_action.lower()
        
        # 計算討好程度
        pleasing_count = sum(
            1 for p in self.PLEASING_PATTERNS 
            if re.search(p.lower(), text)
        )
        
        # 計算誠實程度
        honest_count = sum(
            1 for p in self.HONEST_PATTERNS 
            if re.search(p.lower(), text)
        )
        
        # 計算 phrase score
        total_markers = pleasing_count + honest_count
        if total_markers == 0:
            phrase_score = 0.5  # 中性
        else:
            # 誠實詞彙越多，分數越高
            phrase_score = honest_count / total_markers
        
        # 如果討好程度高但誠實程度低 → 攔截
        if pleasing_count >= 2 and honest_count == 0:
            return AuditResult.INTERCEPT, phrase_score
        
        return AuditResult.PASS, phrase_score
    
    def _calculate_tension(
        self,
        context_score: float,
        phrase_score: float,
    ) -> float:
        """
        計算語義張力
        
        Tension = 1 - (Context * Phrase)^0.5
        """
        combined = context_score * phrase_score
        return 1 - (combined ** 0.5)
    
    def _finalize(
        self,
        audit: BenevolenceAudit,
    ) -> tuple[AuditResult, Optional[str]]:
        """
        最終判定
        """
        # 優先級：REJECT > INTERCEPT > FLAG > PASS
        priority = [
            (audit.shadow_check, "無影子的輸出"),
            (audit.benevolence_check, "攔截無效敘事"),
            (audit.attribute_check, "跨層混用"),
        ]
        
        for result, error_msg in priority:
            if result == AuditResult.REJECT:
                return AuditResult.REJECT, error_msg
            if result == AuditResult.INTERCEPT:
                return AuditResult.INTERCEPT, error_msg
            if result == AuditResult.FLAG:
                return AuditResult.FLAG, error_msg
        
        return AuditResult.PASS, None


# Demo usage
if __name__ == "__main__":
    print("=" * 60)
    print("ToneSoul Benevolence Filter Demo")
    print("=" * 60)
    
    filter = BenevolenceFilter()
    
    # 測試案例
    cases = [
        {
            "name": "Honest Response",
            "action": "I'm not sure about this, but based on limited data...",
            "context": ["data analysis", "uncertainty", "limited information"],
        },
        {
            "name": "Pleasing but Vague",
            "action": "Absolutely! Great question! I'd be happy to help!",
            "context": ["help request"],
        },
        {
            "name": "Shadowless Output",
            "action": "The quantum fluctuations in the temporal matrix...",
            "context": ["weather forecast", "daily news"],
        },
    ]
    
    for case in cases:
        print(f"\n📋 Case: {case['name']}")
        print(f"   Action: {case['action'][:50]}...")
        
        result = filter.audit(
            proposed_action=case["action"],
            context_fragments=case["context"],
        )
        
        print(f"   Result: {result.final_result.value}")
        if result.error_log:
            print(f"   Error: {result.error_log}")
        print(f"   CPT: C={result.context_score:.2f} P={result.phrase_score:.2f} T={result.tension_score:.2f}")
    
    print("\n" + "=" * 60)
