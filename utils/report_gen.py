"""
PDF Report Generator V3 (Comprehensive Intelligence Layer).
Generates detailed, explanatory research reports with full context and analysis.
"""
import io
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak

from utils.dossier_schema import (
    IntelligenceDossier, DossierHeader, IdentitySection, BuildStatusSection,
    TeamMember, FundingRound, FundingSection, AdoptionSection, Milestone, 
    SourceIndexSection, IntelligenceShift
)
from database.models import ProjectStage

class PDFReportGenerator:
    def __init__(self):
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        self.title_style = ParagraphStyle('T', fontSize=28, textColor=colors.black, fontName='Helvetica-Bold', spaceBefore=20, spaceAfter=10)
        self.heading_style = ParagraphStyle('H', fontSize=14, textColor=colors.HexColor('#212121'), fontName='Helvetica-Bold', spaceBefore=15, spaceAfter=8)
        self.subheading_style = ParagraphStyle('SH', fontSize=11, textColor=colors.HexColor('#424242'), fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=5)
        self.body_style = ParagraphStyle('B', fontSize=10, leading=14, textColor=colors.HexColor('#212121'), fontName='Helvetica')
        self.label_style = ParagraphStyle('L', fontSize=9, textColor=colors.HexColor('#757575'), fontName='Helvetica-Bold')
        self.value_style = ParagraphStyle('Val', fontSize=10, fontName='Helvetica')
        self.gap_style = ParagraphStyle('Gap', fontSize=9, textColor=colors.HexColor('#d32f2f'), fontName='Helvetica-Oblique', leftIndent=5)
        self.footer_style = ParagraphStyle('Footer', fontSize=8, textColor=colors.grey, alignment=1)

    def map_project_to_dossier(self, project_info: Dict[str, Any]) -> IntelligenceDossier:
        """Maps raw project info to the strict IntelligenceDossier schema."""
        project = project_info['project']
        funding_rounds = sorted(project_info.get('funding_rounds', []), key=lambda x: x.announced_date if x.announced_date else datetime.min, reverse=True)
        team_members = project_info.get('team_members', [])
        total_raised = project_info.get('total_raised', 0)

        # 1. Determine "Emerging" Signal
        is_emerging = total_raised == 0 and (not project.github_url or not team_members)
        confidence = "Early Signal / Detection" if is_emerging else "High Integrity / Canonical"

        # 2. Header & Verification
        coverage = []
        gaps = []
        verified_scope = []
        
        if total_raised > 0: 
            coverage.append("funding")
            verified_scope.append("funding disclosures")
        else: gaps.append("funding history")
        
        if project.github_url: 
            coverage.append("public repositories")
            verified_scope.append("public codebase existence")
        else: gaps.append("technical transparency")
        
        if project.description: coverage.append("positioning")
        else: gaps.append("detailed system architecture")
        
        if team_members: coverage.append("core personnel")
        else: gaps.append("full team composition")

        header = DossierHeader(
            project_name=project.name,
            category=project.category or "Infrastructure / Cyber Defense",
            scope_domain=project.sector or "Blockchain Ecosystem",
            intelligence_status="Partially Verified" if verified_scope else "Unverified Detection",
            verification_scope=verified_scope,
            information_coverage=coverage,
            explicit_gaps=gaps
        )

        # 3. Identity
        identity = IdentitySection(
            what_it_is=project.description or f"{project.name} is a {project.category or 'infrastructure'} project in its early development phase within the {project.sector or 'blockchain'} layer.",
            problem_it_addresses=self._get_problem_statement(project),
            who_it_is_for=self._get_target_audience(project),
            what_it_is_not=self._get_exclusion_statement(project)
        )

        # 4. Build Status
        stage_factual = f"{project.stage.value.capitalize() if project.stage else ('Emerging' if is_emerging else 'Early-stage')} development"
        build_status = BuildStatusSection(
            repo_url=project.github_url,
            repo_visibility="Public" if project.github_url else "Private/Internal",
            stars=project.github_stars or 0,
            contributors=project.github_contributors or "None detected" if is_emerging else "Limited",
            stage=stage_factual,
            stage_anchors=["web signal detection"] if is_emerging else ["public repository data", "disclosures"]
        )

        # 5. Team
        mapped_members = [TeamMember(name=m.name, role=m.role or "Contributor") for m in team_members]

        # 6. Funding
        mapped_rounds = [
            FundingRound(
                date=r.announced_date,
                round_type=r.round_type.value.capitalize() if r.round_type else "Round",
                amount=f"${r.amount_raised}M" if r.amount_raised else "Undisclosed",
                lead_investor=None
            ) for r in funding_rounds
        ]
        funding = FundingSection(
            total_raised=f"${total_raised:.2f}M" if total_raised > 0 else "Not publicly disclosed",
            history=mapped_rounds,
            lead_investors_summary="Disclosed in project documentation, not fully enumerated in public funding databases." if not is_emerging else "Funding status is currently an unverified gap."
        )

        # 7. Adoption
        metrics = []
        if project.tvl: metrics.append(f"On-chain TVL: ${project.tvl/1e6:.1f}M")
        if project.dau: metrics.append(f"Daily Active Users: {project.dau}")
        adoption = AdoptionSection(
            metrics=metrics,
            context_statement="Adoption and usage metrics are strictly limited to production data or verified on-chain signals."
        )

        # 8. Timeline
        timeline = []
        if project.founded_date:
            timeline.append(Milestone(date=project.founded_date.strftime('%B %Y'), event="Project Founded"))
        for r in reversed(funding_rounds):
            if r.announced_date:
                timeline.append(Milestone(date=r.announced_date.strftime('%B %Y'), event=f"{r.round_type.value.capitalize() if r.round_type else 'Round'} raised"))

        # Data Sources & Signals
        sources_meta = project.data_sources or {}
        hiring_signal = sources_meta.get("hiring_signal", False)
        
        # Build secondary sources from available social signals
        social_links = []
        if project.twitter_handle: social_links.append(f"X/Twitter: @{project.twitter_handle}")
        if project.github_url: social_links.append(f"GitHub: {project.github_url}")
        if project.discord_url: social_links.append(f"Discord: {project.discord_url}")
        if project.telegram_url: social_links.append(f"Telegram: {project.telegram_url}")
        if hiring_signal: social_links.append("Operational Signal: Active Recruitment / Careers Portal detected.")

        sources = SourceIndexSection(
            primary_sources=[project.website] if project.website else [],
            secondary_sources=social_links,
            coverage_gaps=gaps
        )

        # Synthesis
        adoption_metrics = [f"TVL: ${project.tvl:,.2f}"] if project.tvl else []
        if project.dau: adoption_metrics.append(f"User Base: {project.dau:,} DAU")
        
        adoption = AdoptionSection(
            metrics=adoption_metrics,
            context_statement="Adoption and usage metrics are strictly limited to production data or verified on-chain signals."
        )

        return IntelligenceDossier(
            header=header,
            is_emerging=is_emerging,
            identity=IdentitySection(
                what_it_is=project.description or "A protocol or application within the decentralized ecosystem.",
                problem_it_addresses=self._get_problem_statement(project),
                who_it_is_for=self._get_target_audience(project),
                what_it_is_not=self._get_exclusion_statement(project)
            ),
            core_explanation=project.description or f"{project.name} is building infrastructure for the decentralized web.",
            architecture_overview=self._get_architecture_overview(project),
            build_status=BuildStatusSection(
                repo_url=project.github_url,
                repo_visibility="Public" if project.github_url else "Private / Restricted",
                stars=project.github_stars or 0,
                contributors="Active" if project.github_contributors and project.github_contributors > 5 else "Limited" if project.github_contributors else "None detected",
                stage=project.stage.value.capitalize() if project.stage else "Early-stage development",
                stage_anchors=["Product live"] if project.stage == ProjectStage.MAINNET else ["Development cycles"]
            ),
            team_info=f"Official team disclosures are currently { 'partially verified' if project.is_verified else 'limited' }. Personnel primarily operating in public/technical roles.",
            team_members=[TeamMember(name=m.name, role=m.role) for m in project.team_members] if project.team_members else [],
            funding=FundingSection(
                total_raised=f"${total_raised:,.2f}" if total_raised > 0 else "Undisclosed",
                history=[FundingRound(date=r.announced_date, round_type=r.round_type.value.capitalize() if r.round_type else "Round", amount=f"${r.amount_raised:,.2f}" if r.amount_raised else "Undisclosed", lead_investor=None) for r in funding_rounds],
                lead_investors_summary="Direct capital injection from institutional partners." if funding_rounds else "No institutional funding history detected."
            ),
            positioning_statement=f"Positioned as a {project.category or project.sector or 'technical protocol'} within the global ecosystem.",
            integration_status="Publicly confirmed integrations or production partnerships are not yet documented.",
            adoption=adoption,
            risks_unknowns=self._get_risks_and_unknowns(project, funding_rounds),
            timeline=timeline,
            sources=sources,
            intelligence_confidence="Fragmented Signals" if is_emerging else "High Integrity",
            shifts=[IntelligenceShift(date=datetime.utcnow(), type="Detection", description="Initial intelligence capture and baseline synthesis.", impact="Fragmented Signals Established")] if is_emerging else []
        )

    def generate_project_report(self, dossier: IntelligenceDossier) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=15*mm)
        
        story = []
        
        # ============================================================================
        # HEADER
        # ============================================================================
        story.append(Paragraph(dossier.header.project_name, self.title_style))
        story.append(Spacer(1, 6*mm))
        
        status_text = dossier.header.intelligence_status
        scope_text = f"({', '.join(dossier.header.verification_scope).capitalize()})" if dossier.header.verification_scope else "(Source: Web Research Mesh)"
        
        # Flat Metadata
        story.append(Paragraph(f"<b>Category:</b> {dossier.header.category}", self.body_style))
        story.append(Paragraph(f"<b>Scope / Domain:</b> {dossier.header.scope_domain}", self.body_style))
        story.append(Paragraph(f"<b>Last Updated:</b> {dossier.header.last_updated.strftime('%B %d, %Y – %H:%M UTC')}", self.body_style))
        story.append(Paragraph(f"<b>Intelligence Status:</b> {status_text} {scope_text}", self.body_style))
        story.append(Paragraph(f"<b>Intelligence Confidence:</b> <i>{dossier.intelligence_confidence}</i>", self.body_style))
        
        coverage_text = ", ".join(dossier.header.information_coverage).capitalize() if dossier.header.information_coverage else "Minimal disclosures"
        story.append(Paragraph(f"<b>Information Coverage:</b> {coverage_text}", self.body_style))
        
        gap_text = ", ".join(dossier.header.explicit_gaps).capitalize() if dossier.header.explicit_gaps else "None identified"
        story.append(Paragraph(f"<b>Explicit Gaps:</b> <font color='#d32f2f'>{gap_text}</font>", self.body_style))
        
        story.append(Spacer(1, 10*mm))

        # 1. Identity & Scope
        story.append(Paragraph("1. Identity & Scope", self.heading_style))
        story.append(Paragraph("<b>What it is</b>", self.subheading_style))
        story.append(Paragraph(dossier.identity.what_it_is, self.body_style))
        story.append(Paragraph("<b>Problem it addresses</b>", self.subheading_style))
        story.append(Paragraph(dossier.identity.problem_it_addresses, self.body_style))
        story.append(Paragraph("<b>Who it is for</b>", self.subheading_style))
        story.append(Paragraph(dossier.identity.who_it_is_for, self.body_style))
        story.append(Paragraph("<b>What it is not</b>", self.subheading_style))
        story.append(Paragraph(dossier.identity.what_it_is_not, self.body_style))
        story.append(Spacer(1, 5*mm))

        # 2. What They Are Building
        story.append(Paragraph("2. What They Are Building (Core Explanation)", self.heading_style))
        story.append(Paragraph(dossier.core_explanation, self.body_style))
        story.append(Spacer(1, 5*mm))

        # 3. Architecture Overview
        story.append(Paragraph("3. Architecture Overview (High Level)", self.heading_style))
        story.append(Paragraph(dossier.architecture_overview, self.body_style))
        story.append(Spacer(1, 5*mm))

        # 4. Current Build Status
        story.append(Paragraph("4. Current Build Status", self.heading_style))
        story.append(Paragraph("<b>Codebase</b>", self.subheading_style))
        repo_val = dossier.build_status.repo_url or "<font color='#d32f2f'>Not fully disclosed</font>"
        story.append(Paragraph(f"• Repository: {repo_val}", self.body_style))
        story.append(Paragraph(f"• Visibility: {dossier.build_status.repo_visibility}", self.body_style))
        story.append(Paragraph("<b>Development signals</b>", self.subheading_style))
        story.append(Paragraph(f"• Engagement: {dossier.build_status.stars} stars, {dossier.build_status.contributors} contributors", self.body_style))
        story.append(Paragraph("<b>Deployment status</b>", self.subheading_style))
        story.append(Paragraph(f"• Stage: {dossier.build_status.stage} (Anchored by {', '.join(dossier.build_status.stage_anchors)})", self.body_style))
        story.append(Spacer(1, 5*mm))

        # 5. Team & Contributors
        story.append(Paragraph("5. Team & Contributors", self.heading_style))
        if dossier.team_members:
            for member in dossier.team_members:
                story.append(Paragraph(f"• <b>{member.name}</b> – {member.role}", self.body_style))
        else:
            story.append(Paragraph(dossier.team_info, self.body_style))
        story.append(Spacer(1, 5*mm))

        # 6. Funding & Backers
        story.append(Paragraph("6. Funding & Backers", self.heading_style))
        story.append(Paragraph(f"<b>Total Funding Raised:</b> {dossier.funding.total_raised}", self.body_style))
        if dossier.funding.history:
            story.append(Paragraph("<b>Funding History</b>", self.subheading_style))
            for r in dossier.funding.history:
                story.append(Paragraph(f"• {r.date.strftime('%B %d, %Y') if r.date else 'Date N/A'} – {r.round_type} – {r.amount}", self.body_style))
            story.append(Paragraph("<b>Lead Investors</b>", self.subheading_style))
            story.append(Paragraph(dossier.funding.lead_investors_summary, self.body_style))
        elif dossier.is_emerging:
             story.append(Paragraph("<i>No confirmed institutional funding history detected. Project may be in stealth or self-funded pre-seed phase.</i>", self.body_style))
        story.append(Spacer(1, 5*mm))

        # 7. Ecosystem Positioning
        story.append(Paragraph("7. Ecosystem Positioning", self.heading_style))
        story.append(Paragraph(dossier.positioning_statement, self.body_style))
        story.append(Paragraph(dossier.integration_status, self.body_style))
        story.append(Spacer(1, 5*mm))

        # 8. Adoption & Usage
        story.append(Paragraph("8. Adoption & Usage", self.heading_style))
        if dossier.adoption.metrics:
            for m in dossier.adoption.metrics: story.append(Paragraph(f"• {m}", self.body_style))
        else:
            story.append(Paragraph("Adoption and usage metrics are not publicly available at this time.", self.body_style))
        story.append(Spacer(1, 5*mm))

        # 9. Risks, Constraints & Unknowns
        story.append(Paragraph("9. Risks, Constraints & Unknowns", self.heading_style))
        for r in dossier.risks_unknowns:
            story.append(Paragraph(r, self.body_style))
            story.append(Spacer(1, 2*mm))
        story.append(Spacer(1, 5*mm))

        # 10. Timeline & Milestones
        story.append(Paragraph("10. Timeline & Milestones", self.heading_style))
        timeline_items = sorted(dossier.timeline, key=lambda x: x.date, reverse=True)
        if timeline_items:
            for m in timeline_items:
                story.append(Paragraph(f"• {m.date}: {m.event}", self.body_style))
        else:
            story.append(Paragraph("Initial detection signal. Full development timeline is not yet publicly documented.", self.body_style))
        story.append(Spacer(1, 5*mm))

        # 11. Source Index & Transparency
        story.append(Paragraph("11. Source Index & Transparency", self.heading_style))
        story.append(Paragraph("<b>Primary Sources</b>", self.subheading_style))
        if dossier.sources.primary_sources:
            for s in dossier.sources.primary_sources: story.append(Paragraph(f"• {s}", self.body_style))
        else:
            story.append(Paragraph("<font color='#d32f2f'><i>Direct documentation is currently restricted or unpublished.</i></font>", self.body_style))
        story.append(Paragraph("<b>Secondary Sources</b>", self.subheading_style))
        for s in dossier.sources.secondary_sources: story.append(Paragraph(f"• {s}", self.body_style))
        story.append(Paragraph("<b>Coverage Gaps</b>", self.subheading_style))
        if dossier.sources.coverage_gaps:
            for g in dossier.sources.coverage_gaps: story.append(Paragraph(f"• <font color='#d32f2f'>{g.capitalize()}</font>", self.body_style))
        else:
            story.append(Paragraph("No critical intelligence gaps identified.", self.body_style))
        story.append(Spacer(1, 5*mm))

        # 12. How to Read This Dossier
        story.append(Paragraph("12. How to Read This Dossier", self.heading_style))
        story.append(Paragraph(dossier.reading_guide, self.body_style))
        story.append(Spacer(1, 5*mm))

        # 13. Intelligence Shifts (Temporal Intelligence)
        story.append(Paragraph("13. Intelligence Shifts", self.heading_style))
        if dossier.shifts:
            for shift in dossier.shifts:
                story.append(Paragraph(f"• <b>{shift.date.strftime('%B %d, %Y')}</b>: {shift.type} shift detected.", self.body_style))
                story.append(Paragraph(f"<i>{shift.description}</i> (Impact: {shift.impact})", self.body_style))
        else:
            story.append(Paragraph("Initial synthesis cycle. No chronological shifts detected since baseline intelligence capture.", self.body_style))
        
        # Footer
        story.append(Spacer(1, 10*mm))
        story.append(Paragraph(f"<b>{dossier.effective_footer}</b>", self.footer_style))
        story.append(Paragraph(f"FundFlow Intelligence Platform | {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC", self.footer_style))

        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _get_problem_statement(self, project):
        cat = (project.category or "").lower()
        if not project.description:
            if "security" in cat: return "Current blockchain security models rely heavily on reactive manual intervention, creating a window of vulnerability between threat detection and response as protocols lack automated defensive logic."
            return f"The {project.sector or 'blockchain'} sector faces complexity in operationalizing {project.category or 'infrastructure'} without standardized, automated frameworks, necessitating a shift toward deterministic execution layers."
        return f"Most systems in the {project.sector or 'blockchain'} layer rely on preventative or reactive manual oversight. {project.name} targets the gap between discovery and execution by providing a structured, programmable framework for automating {project.category or 'this domain'}."

    def _get_target_audience(self, project):
        cat = (project.category or "").lower()
        if "security" in cat or "infra" in cat: return "Core protocol teams, DAO security committees, and institutional infrastructure providers managing production smart-contract systems."
        if "defi" in cat: return "Liquidity providers, yield optimizers, and decentralized exchange participants seeking risk-managed exposure."
        return "Early adoption is targeting institutional and developer-centric ecosystem participants."

    def _get_exclusion_statement(self, project):
        cat = (project.category or "").lower()
        if "security" in cat: return "This project is not a traditional audit firm, a consumer-facing monitoring dashboard, or a post-mortem analytics tool."
        if "infra" in cat: return "This is not a retail-facing application or trading interface."
        return "This project is not a retail-focused consumer application."

    def _get_building_explanation(self, project):
        cat = (project.category or "").lower()
        article = "an" if "ethereum" in cat or "infra" in cat or cat.startswith('e') else "a"
        if not project.description:
            return f"{project.name} is building a programmable layer for {project.category or 'decentralized infrastructure'} that enables protocols to define logic and trigger predefined actions under specific on-chain conditions. The system appears intended to operate as security middleware."
        return f"{project.name} is building {article} {project.category or 'system'} designed to enable {project.description}. The system aims to shift {project.sector or 'blockchain'} operations from manual oversight to deterministic, logic-driven execution, operating as programmable middleware."

    def _get_architecture_overview(self, project):
        return "Public documentation suggests a modular architecture consisting of detection logic (traps), evaluation nodes, and execution contracts. These components appear intended to separate threat definition, condition evaluation, and response execution responsibilities for deterministic defensive scaling."

    def _get_risks_and_unknowns(self, project, funding):
        risks = [
            "• Effectiveness of automated logic in novel exploit scenarios or complex market conditions is unproven publicly.",
            "• Integration complexity and operational overhead for protocol teams is currently unquantified due to early-stage documentation.",
            "• Governance, control mechanisms, and decentralization roadmap details are not fully disclosed in current technical specifications.",
            "• Adoption trajectory remains unclear pending wide-scale production deployments and verified usage case studies."
        ]
        if not project.github_url:
            risks.append("• Technical transparency risk: Core codebase is not available for independent verification via public repositories.")
        if not funding:
            risks.append("• Financial sustainability risk: No confirmed institutional funding rounds or capital reserves disclosed.")
        return risks
    
