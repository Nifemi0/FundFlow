from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class DossierHeader(BaseModel):
    project_name: str
    category: str
    scope_domain: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    intelligence_status: str # e.g., "Partially Verified", "Unverified Detection"
    verification_scope: List[str] # e.g., ["funding disclosures", "public codebase existence"]
    information_coverage: List[str]
    explicit_gaps: List[str]

class IdentitySection(BaseModel):
    what_it_is: str
    problem_it_addresses: str
    who_it_is_for: str
    what_it_is_not: str

class BuildStatusSection(BaseModel):
    repo_url: Optional[str]
    repo_visibility: str # "Public", "Private", "Internal"
    stars: int = 0
    contributors: str # e.g. "Limited", "Active", "None detected"
    stage: str # e.g. "Early-stage development"
    stage_anchors: List[str] # e.g. ["public repository data", "disclosures"]

class TeamMember(BaseModel):
    name: str
    role: str

class FundingRound(BaseModel):
    date: Optional[datetime]
    round_type: str
    amount: str # e.g. "$1.55M"
    lead_investor: Optional[str]

class FundingSection(BaseModel):
    total_raised: str # e.g. "$6.30M"
    history: List[FundingRound]
    lead_investors_summary: str

class AdoptionSection(BaseModel):
    metrics: List[str] # e.g. ["On-chain TVL: $1.2M", "Daily Active Users: 150"]
    context_statement: str

class Milestone(BaseModel):
    date: str
    event: str

class SourceIndexSection(BaseModel):
    primary_sources: List[str]
    secondary_sources: List[str]
    coverage_gaps: List[str]

class IntelligenceShift(BaseModel):
    date: datetime
    type: str # e.g., "Funding", "Codebase", "Stage", "Detection"
    description: str
    impact: str # e.g., "Expanded Coverage", "Increased Confidence", "New Gap Identified"

class IntelligenceDossier(BaseModel):
    header: DossierHeader
    is_emerging: bool = False
    
    # 1. Identity & Scope
    identity: IdentitySection
    
    # 2. What They Are Building
    core_explanation: str
    
    # 3. Architecture Overview
    architecture_overview: str # Should explain roles/responsibilities
    
    # 4. Current Build Status
    build_status: BuildStatusSection
    
    # 5. Team & Contributors
    team_info: str # Summary or list description
    team_members: List[TeamMember]
    
    # 6. Funding & Backers
    funding: FundingSection
    
    # 7. Ecosystem Positioning
    positioning_statement: str
    integration_status: str
    
    # 8. Adoption & Usage
    adoption: AdoptionSection
    
    # 9. Risks, Constraints & Unknowns
    risks_unknowns: List[str]
    
    # 10. Timeline & Milestones
    timeline: List[Milestone]
    
    # 11. Source Index & Transparency
    sources: SourceIndexSection
    
    # 12. How to Read This Dossier
    reading_guide: str = "This document is a factual streamlining of available intelligence. It is not an endorsement, prediction, or judgment. Gaps in data are explicitly stated to prevent misinterpretation of partial information. All data is time-stamped as per the 'Last Updated' header. Confidence refers to the integrity of the collection process, not project success."

    # 13. Intelligence Shifts (Temporal Intelligence)
    shifts: List[IntelligenceShift] = []

    footer_label: str = "INTERNAL RESEARCH DOSSIER"
    
    # Standardized: "Canonical", "High Integrity", "Partial Coverage", "Fragmented Signals"
    intelligence_confidence: str = "High Integrity" 

    @property
    def effective_footer(self) -> str:
        return "EMERGING PROJECT DETECTION" if self.is_emerging else "INTERNAL RESEARCH DOSSIER"
