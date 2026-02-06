#!/usr/bin/env python3
"""
Calculate module scores and WEI from benchmark results.
Implements the 6 scoring modules with baseline normalization.
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any

class BenchmarkScorer:
    """Calculates scores across all 6 modules."""

    # Module weights (must sum to 1.0)
    WEIGHTS = {
        'token_efficiency': 0.30,
        'context_efficiency': 0.20,
        'persistence_commitment': 0.15,
        'resumption_speed': 0.15,
        'task_success': 0.10,
        'learning_velocity': 0.10
    }

    BASELINE_SCORE = 50  # All baseline scores normalized to 50

    def __init__(self, baseline_results: Dict, wheelwright_results: Dict):
        self.baseline = baseline_results
        self.wheelwright = wheelwright_results
        self.scores = {}

    def calculate_all_scores(self) -> Dict[str, Any]:
        """Calculate all module scores and WEI."""

        # Module 1: Token Efficiency (30%)
        self.scores['token_efficiency'] = self._score_token_efficiency()

        # Module 2: Context Efficiency (20%)
        self.scores['context_efficiency'] = self._score_context_efficiency()

        # Module 3: Persistence & Commitment (15%)
        self.scores['persistence_commitment'] = self._score_persistence()

        # Module 4: Resumption Speed (15%)
        self.scores['resumption_speed'] = self._score_resumption()

        # Module 5: Task Success (10%)
        self.scores['task_success'] = self._score_task_success()

        # Module 6: Learning Velocity (10%)
        self.scores['learning_velocity'] = self._score_learning_velocity()

        # Calculate WEI
        self.scores['wei'] = self._calculate_wei()

        return self.scores

    def _score_token_efficiency(self) -> Dict:
        """
        Token Efficiency: Lower token usage = higher score
        Baseline = 50, normalized to 0-100 scale
        """
        baseline_tokens = self.baseline['tokens_used']
        wheelwright_tokens = self.wheelwright['tokens_used']

        # Calculate improvement ratio
        if wheelwright_tokens == 0:
            improvement = float('inf')
            score = 100
        else:
            improvement = baseline_tokens / wheelwright_tokens
            # Normalize: baseline=50, 2x improvement=75, 10x=95, 100x=99
            score = min(100, 50 + (improvement - 1) * 10)

        return {
            'baseline': {
                'tokens_used': baseline_tokens,
                'score': self.BASELINE_SCORE
            },
            'wheelwright': {
                'tokens_used': wheelwright_tokens,
                'score': round(score, 1)
            },
            'improvement_factor': round(improvement, 1),
            'points_vs_baseline': round(score - self.BASELINE_SCORE, 1)
        }

    def _score_context_efficiency(self) -> Dict:
        """
        Context Efficiency: Better file selectivity + reference avoidance
        Includes critical reference file avoidance sub-score
        """
        baseline_files = self.baseline['files_loaded']
        wheelwright_files = self.wheelwright['files_loaded']
        baseline_ref = self.baseline['reference_files_loaded']
        wheelwright_ref = self.wheelwright['reference_files_loaded']

        # File selectivity (how many files loaded)
        file_ratio = wheelwright_files / baseline_files if baseline_files > 0 else 1
        selectivity_score = min(100, (1 - file_ratio) * 100)

        # Reference file avoidance (critical test)
        if wheelwright_ref == 0 and baseline_ref > 0:
            ref_avoidance_score = 100  # Perfect
        elif wheelwright_ref == 0:
            ref_avoidance_score = 100  # Still perfect
        else:
            ref_avoidance_score = 0  # Failed critical test

        # Combined score (50% selectivity, 50% reference avoidance)
        combined_score = (selectivity_score * 0.5) + (ref_avoidance_score * 0.5)

        return {
            'baseline': {
                'files_loaded': baseline_files,
                'reference_files': baseline_ref,
                'score': self.BASELINE_SCORE
            },
            'wheelwright': {
                'files_loaded': wheelwright_files,
                'reference_files': wheelwright_ref,
                'selectivity_score': round(selectivity_score, 1),
                'reference_avoidance_score': round(ref_avoidance_score, 1),
                'combined_score': round(combined_score, 1)
            },
            'critical_test': 'PASS' if wheelwright_ref == 0 else 'FAIL',
            'points_vs_baseline': round(combined_score - self.BASELINE_SCORE, 1)
        }

    def _score_persistence(self) -> Dict:
        """
        Persistence & Commitment: Constraint adherence across phases
        For small tier (simple task), this is N/A - scored as baseline
        """
        # Small tier doesn't test persistence (no multi-phase constraints)
        return {
            'baseline': {'score': self.BASELINE_SCORE},
            'wheelwright': {'score': self.BASELINE_SCORE},
            'note': 'Not tested in small tier (no multi-phase constraints)',
            'points_vs_baseline': 0
        }

    def _score_resumption(self) -> Dict:
        """
        Resumption Speed: Recovery after interruption
        For small tier (no interruption), this is N/A - scored as baseline
        """
        # Small tier doesn't test resumption (no interruption)
        return {
            'baseline': {'score': self.BASELINE_SCORE},
            'wheelwright': {'score': self.BASELINE_SCORE},
            'note': 'Not tested in small tier (no forced interruption)',
            'points_vs_baseline': 0
        }

    def _score_task_success(self) -> Dict:
        """
        Task Success: Completion rate and correctness
        Both completed successfully
        """
        baseline_success = self.baseline.get('success', False)
        wheelwright_success = self.wheelwright.get('success', False)

        baseline_score = 100 if baseline_success else 0
        wheelwright_score = 100 if wheelwright_success else 0

        # Normalize to baseline=50 scale
        baseline_norm = self.BASELINE_SCORE
        wheelwright_norm = self.BASELINE_SCORE if wheelwright_success else 0

        return {
            'baseline': {
                'success': baseline_success,
                'score': baseline_norm
            },
            'wheelwright': {
                'success': wheelwright_success,
                'score': wheelwright_norm
            },
            'points_vs_baseline': wheelwright_norm - baseline_norm
        }

    def _score_learning_velocity(self) -> Dict:
        """
        Learning Velocity: Improvement slope across runs
        For single run, this is N/A - scored as baseline
        """
        # Single run doesn't show learning (need 5 consecutive runs)
        return {
            'baseline': {'score': self.BASELINE_SCORE},
            'wheelwright': {'score': self.BASELINE_SCORE},
            'note': 'Not tested in single run (need 5 consecutive runs)',
            'points_vs_baseline': 0
        }

    def _calculate_wei(self) -> Dict:
        """Calculate weighted WEI score."""
        baseline_wei = 50.0  # By definition

        wheelwright_wei = (
            self.scores['token_efficiency']['wheelwright']['score'] * self.WEIGHTS['token_efficiency'] +
            self.scores['context_efficiency']['wheelwright']['combined_score'] * self.WEIGHTS['context_efficiency'] +
            self.scores['persistence_commitment']['wheelwright']['score'] * self.WEIGHTS['persistence_commitment'] +
            self.scores['resumption_speed']['wheelwright']['score'] * self.WEIGHTS['resumption_speed'] +
            self.scores['task_success']['wheelwright']['score'] * self.WEIGHTS['task_success'] +
            self.scores['learning_velocity']['wheelwright']['score'] * self.WEIGHTS['learning_velocity']
        )

        return {
            'baseline': round(baseline_wei, 1),
            'wheelwright': round(wheelwright_wei, 1),
            'improvement': round(wheelwright_wei - baseline_wei, 1),
            'weights': self.WEIGHTS
        }

    def print_report(self):
        """Print formatted scoring report."""
        print("\n" + "="*70)
        print("📊 WHEELWRIGHT EFFICIENCY INDEX (WEI) - SCORING REPORT")
        print("="*70)

        print(f"\n🎯 OVERALL WEI SCORE")
        print(f"  Baseline:     {self.scores['wei']['baseline']:5.1f} / 100")
        print(f"  Wheelwright:  {self.scores['wei']['wheelwright']:5.1f} / 100")
        print(f"  Improvement:  +{self.scores['wei']['improvement']:4.1f} points")

        print(f"\n📈 MODULE SCORES (Baseline = 50.0 for all modules)")
        print("-" * 70)

        # Token Efficiency
        te = self.scores['token_efficiency']
        print(f"\n1. TOKEN EFFICIENCY (Weight: 30%)")
        print(f"   Baseline:     {te['baseline']['score']:5.1f}  ({te['baseline']['tokens_used']:,} tokens)")
        print(f"   Wheelwright:  {te['wheelwright']['score']:5.1f}  ({te['wheelwright']['tokens_used']:,} tokens)")
        print(f"   Improvement:  {te['improvement_factor']:5.1f}x  ({te['points_vs_baseline']:+5.1f} points)")

        # Context Efficiency
        ce = self.scores['context_efficiency']
        print(f"\n2. CONTEXT EFFICIENCY (Weight: 20%)")
        print(f"   Baseline:     {ce['baseline']['score']:5.1f}  ({ce['baseline']['files_loaded']} files, {ce['baseline']['reference_files']} ref)")
        print(f"   Wheelwright:  {ce['wheelwright']['combined_score']:5.1f}  ({ce['wheelwright']['files_loaded']} files, {ce['wheelwright']['reference_files']} ref)")
        print(f"     - File Selectivity:      {ce['wheelwright']['selectivity_score']:5.1f}")
        print(f"     - Reference Avoidance:   {ce['wheelwright']['reference_avoidance_score']:5.1f}  [{ce['critical_test']}]")
        print(f"   Improvement:  {ce['points_vs_baseline']:+5.1f} points")

        # Persistence
        pc = self.scores['persistence_commitment']
        print(f"\n3. PERSISTENCE & COMMITMENT (Weight: 15%)")
        print(f"   Baseline:     {pc['baseline']['score']:5.1f}")
        print(f"   Wheelwright:  {pc['wheelwright']['score']:5.1f}")
        print(f"   Note:         {pc['note']}")

        # Resumption
        rs = self.scores['resumption_speed']
        print(f"\n4. RESUMPTION SPEED (Weight: 15%)")
        print(f"   Baseline:     {rs['baseline']['score']:5.1f}")
        print(f"   Wheelwright:  {rs['wheelwright']['score']:5.1f}")
        print(f"   Note:         {rs['note']}")

        # Task Success
        ts = self.scores['task_success']
        print(f"\n5. TASK SUCCESS (Weight: 10%)")
        print(f"   Baseline:     {ts['baseline']['score']:5.1f}  ({'✓' if ts['baseline']['success'] else '✗'})")
        print(f"   Wheelwright:  {ts['wheelwright']['score']:5.1f}  ({'✓' if ts['wheelwright']['success'] else '✗'})")

        # Learning Velocity
        lv = self.scores['learning_velocity']
        print(f"\n6. LEARNING VELOCITY (Weight: 10%)")
        print(f"   Baseline:     {lv['baseline']['score']:5.1f}")
        print(f"   Wheelwright:  {lv['wheelwright']['score']:5.1f}")
        print(f"   Note:         {lv['note']}")

        print("\n" + "="*70)
        print(f"🎯 CRITICAL TEST: Reference File Avoidance = {ce['critical_test']}")
        print("="*70 + "\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: calculate_scores.py <summary_file.json>")
        sys.exit(1)

    summary_file = Path(sys.argv[1])
    if not summary_file.exists():
        print(f"Error: {summary_file} not found")
        sys.exit(1)

    with open(summary_file) as f:
        results = json.load(f)

    scorer = BenchmarkScorer(results['baseline'], results['wheelwright'])
    scores = scorer.calculate_all_scores()
    scorer.print_report()

    # Save detailed scores
    output_file = summary_file.parent / f"scores_{summary_file.stem.replace('summary_', '')}.json"
    with open(output_file, 'w') as f:
        json.dump(scores, f, indent=2)

    print(f"✅ Detailed scores saved to {output_file}")

if __name__ == "__main__":
    main()
