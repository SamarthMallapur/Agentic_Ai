import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from schemas.report import PlacementReport, MarketTrend, ReportClaim, RecommendedAction
from memory.profile_memory import ProfileMemory
from tools.market_analysis import MarketAnalysis
from tools.application_tracker import ApplicationTracker

def generate_weekly_report() -> PlacementReport:
    # 1. Gather Data
    profile_db = ProfileMemory()
    market_db = MarketAnalysis()
    app_db = ApplicationTracker()
    
    profile = profile_db.get_profile()
    market = market_db.get_market_statistics()
    apps = app_db.get_applications()
    
    # Process Applications
    total_apps = len(apps)
    interviews = len([a for a in apps if a.get('status') in ['INTERVIEW', 'TECHNICAL_INTERVIEW', 'HR_INTERVIEW']])
    offers = len([a for a in apps if a.get('status') == 'OFFER'])
    rejections = len([a for a in apps if a.get('status') == 'REJECTED'])
    
    resume_scores = [a.get('resume_score') for a in apps if a.get('resume_score') is not None]
    avg_score = sum(resume_scores) / len(resume_scores) if resume_scores else 0
    highest_score = max(resume_scores) if resume_scores else 0
    lowest_score = min(resume_scores) if resume_scores else 0
    
    # Process Market
    top_skills = [s[0] for s in market.get('top_skills', [])]
    roles = [r[0] for r in market.get('common_roles', [])]
    
    market_trends = MarketTrend(
        top_skills=top_skills,
        rising_skills=[],
        common_roles=roles,
        relevant_technologies=[]
    )
    
    # Skill Gaps
    student_skills = set([s.lower() for s in profile.get('technical_skills', [])])
    demand_comparison = {}
    for skill, pct in market.get('skill_demand_percentage', {}).items():
        if pct > 10:  # Only show skills > 10%
            demand_comparison[skill] = skill.lower() in student_skills
            
    # Evidence
    evidence_table = []
    if market.get('total_jobs_analyzed', 0) > 0:
        for skill, pct in market.get('skill_demand_percentage', {}).items():
            if pct > 20:
                evidence_table.append(ReportClaim(
                    claim=f"{skill} is highly demanded",
                    evidence=f"{pct}% of postings contain {skill}",
                    source="Local Job Dataset",
                    sample_size=market['total_jobs_analyzed'],
                    confidence="High"
                ))

    # Recommendations
    recommendations = []
    missing_top_skills = [k for k, v in demand_comparison.items() if not v and market['skill_demand_percentage'][k] > 20]
    if missing_top_skills:
        skill = missing_top_skills[0]
        recommendations.append(RecommendedAction(
            action=f"Learn {skill}",
            why=f"{skill} is frequently requested but missing from your profile.",
            evidence=f"Appears in {market['skill_demand_percentage'][skill]}% of jobs.",
            effort="Medium",
            expected_benefit="Increase ATS match rate significantly."
        ))

    return PlacementReport(
        total_applications=total_apps,
        interviews=interviews,
        offers=offers,
        rejections=rejections,
        average_resume_score=avg_score,
        highest_resume_score=highest_score,
        lowest_resume_score=lowest_score,
        most_common_weaknesses=profile.get('weak_areas', []),
        market_trends=market_trends,
        market_demand_comparison=demand_comparison,
        strong_areas=profile.get('technical_skills', [])[:3],
        weak_areas=profile.get('weak_areas', []),
        frequently_missed_questions=[],
        recommended_actions=recommendations,
        evidence_table=evidence_table
    )
