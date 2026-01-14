"""
Message formatters for Telegram bot responses.
Formats database objects into readable Telegram messages with HTML.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from html import escape
from database.models import Project, FundingRound, Investor

def format_project_summary(project: Project) -> str:
    """Format a project as a brief summary."""
    grade_emoji = {
        "A+": "🏆",
        "A": "⭐",
        "B": "✨",
        "C": "📊",
        "D": "📉"
    }
    
    emoji = grade_emoji.get(project.grade_letter, "📁")
    
    summary = f"{emoji} <b>{escape(project.name)}</b>"
    
    if project.grade_letter:
        summary += f" <code>{escape(project.grade_letter)}</code>"
    
    if project.sector:
        summary += f"\n🏷️ {escape(project.sector)}"
        if project.category:
            summary += f" › {escape(project.category)}"
    
    if project.description:
        desc = project.description[:150]
        if len(project.description) > 150:
            desc += "..."
        summary += f"\n<i>{escape(desc)}</i>"
    
    if project.website:
        summary += f"\n🔗 {escape(project.website)}"
    
    return summary


def format_funding_round(project: Project, funding_round: FundingRound) -> str:
    """Format a funding round announcement."""
    # Amount formatting
    amount_str = f"${funding_round.amount_raised:.1f}M" if funding_round.amount_raised else "Undisclosed"
    
    # Round type formatting
    round_type = funding_round.round_type.value.replace("_", " ").title()
    
    # Date formatting
    date_str = funding_round.announced_date.strftime("%b %d, %Y")
    
    # Build message
    msg = f"💰 **{project.name}** raised **{amount_str}**\n"
    msg += f"📊 {round_type}\n"
    msg += f"📅 {date_str}\n"
    
    # Lead investor
    if funding_round.lead_investor:
        msg += f"🎯 Led by: **{funding_round.lead_investor.name}**\n"
    
    # Other investors
    if funding_round.investors and len(funding_round.investors) > 1:
        other_investors = [inv.name for inv in funding_round.investors if inv.id != (funding_round.lead_investor_id or 0)]
        if other_investors:
            investors_str = ", ".join(other_investors[:3])
            if len(other_investors) > 3:
                investors_str += f" +{len(other_investors) - 3} more"
            msg += f"🤝 Participants: {investors_str}\n"
    
    # Project details
    if project.sector:
        msg += f"🏷️ {project.sector}"
        if project.category:
            msg += f" › {project.category}"
        msg += "\n"
    
    # Grade
    if project.grade_letter:
        grade_desc = {
            "A+": "Exceptional",
            "A": "Excellent",
            "B": "Strong",
            "C": "Average",
            "D": "Below Average"
        }
        msg += f"⭐ Grade: **{project.grade_letter}** ({grade_desc.get(project.grade_letter, '')})\n"
    
    return msg.strip()


def format_investor_profile(investor: Investor, portfolio: List[Dict[str, Any]]) -> str:
    """Format investor profile with portfolio."""
    msg = f"💼 **{investor.name}**\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Investor details
    if investor.type:
        msg += f"**Type:** {investor.type}\n"
    
    if investor.headquarters:
        msg += f"**HQ:** {investor.headquarters}\n"
    
    if investor.tier:
        tier_desc = {1: "🏆 Tier 1 (Top)", 2: "⭐ Tier 2", 3: "✨ Tier 3"}
        msg += f"**Tier:** {tier_desc.get(investor.tier, f'Tier {investor.tier}')}\n"
    
    msg += f"**Total Investments:** {investor.total_investments or 'Unknown'}\n"
    
    if investor.website:
        msg += f"**Website:** {investor.website}\n"
    
    msg += "\n📊 **Recent Portfolio:**\n\n"
    
    # Portfolio
    if not portfolio:
        msg += "_No recent investments found._"
    else:
        for i, item in enumerate(portfolio[:10], 1):
            project = item["project"]
            funding_round = item["funding_round"]
            
            amount_str = f"${funding_round.amount_raised:.1f}M" if funding_round.amount_raised else "Undisclosed"
            round_type = funding_round.round_type.value.replace("_", " ").title()
            date_str = funding_round.announced_date.strftime("%b %Y")
            
            msg += f"{i}. **{project.name}** · {amount_str} {round_type}\n"
            msg += f"   {date_str}"
            if project.sector:
                msg += f" · {project.sector}"
            msg += "\n\n"
    
    msg += f"\n_Use `/report <project>` for detailed project analysis._"
    
    return msg


def format_full_report(project_info: Dict[str, Any]) -> str:
    """Format a complete project research report."""
    project = project_info["project"]
    funding_rounds = project_info["funding_rounds"]
    team_members = project_info["team_members"]
    total_raised = project_info["total_raised"]
    latest_round = project_info["latest_round"]
    
    msg = f"📄 **PROJECT REPORT: {project.name}**\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # === OVERVIEW ===
    msg += "**📌 OVERVIEW**\n"
    if project.description:
        msg += f"{project.description}\n\n"
    
    if project.sector:
        msg += f"**Sector:** {project.sector}\n"
    if project.category:
        msg += f"**Category:** {project.category}\n"
    if project.stage:
        msg += f"**Stage:** {project.stage.value.title()}\n"
    if project.website:
        msg += f"**Website:** {project.website}\n"
    
    msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # === FUNDING ===
    msg += "**💰 FUNDING HISTORY**\n"
    msg += f"**Total Raised:** ${total_raised:.1f}M\n"
    msg += f"**Funding Rounds:** {len(funding_rounds)}\n\n"
    
    if funding_rounds:
        # Sort by date
        sorted_rounds = sorted(funding_rounds, key=lambda x: x.announced_date, reverse=True)
        
        for round in sorted_rounds[:5]:  # Show last 5 rounds
            amount = f"${round.amount_raised:.1f}M" if round.amount_raised else "Undisclosed"
            round_type = round.round_type.value.replace("_", " ").title()
            date = round.announced_date.strftime("%b %Y")
            
            msg += f"• **{round_type}** · {amount} · {date}\n"
            if round.lead_investor:
                msg += f"  Led by: {round.lead_investor.name}\n"
            if round.valuation:
                msg += f"  Valuation: ${round.valuation:.0f}M ({round.valuation_type or 'N/A'})\n"
            msg += "\n"
    
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # === TEAM ===
    msg += "**👥 TEAM**\n"
    
    if team_members:
        for member in team_members[:5]:  # Show top 5 team members
            msg += f"• **{member.name}**"
            if member.role:
                msg += f" · {member.role}"
            msg += "\n"
            
            if member.previous_companies:
                prev = ", ".join(member.previous_companies[:3])
                msg += f"  Previously: {prev}\n"
            msg += "\n"
    else:
        msg += "_Team information not available._\n"
    
    msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # === TRACTION ===
    msg += "**📈 TRACTION METRICS**\n"
    
    if project.github_url:
        msg += f"**GitHub:** {project.github_url}\n"
        if project.github_stars:
            msg += f"  ⭐ Stars: {project.github_stars:,}\n"
        if project.github_forks:
            msg += f"  🔱 Forks: {project.github_forks:,}\n"
        if project.github_contributors:
            msg += f"  👥 Contributors: {project.github_contributors}\n"
        msg += "\n"
    
    if project.twitter_handle:
        msg += f"**Twitter:** @{project.twitter_handle}\n"
        if project.twitter_followers:
            msg += f"  👥 Followers: {project.twitter_followers:,}\n"
        msg += "\n"
    
    # Token metrics
    if project.has_token and project.token_symbol:
        msg += f"**Token:** ${project.token_symbol}\n"
        if project.token_address:
            msg += f"  Address: `{project.token_address[:10]}...`\n"
        msg += "\n"
    
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # === GRADE ===
    if project.grade_letter:
        grade_desc = {
            "A+": "🏆 Exceptional - Top-tier VCs, proven team, strong traction",
            "A": "⭐ Excellent - Strong fundamentals across all metrics",
            "B": "✨ Strong - Good project with solid backing",
            "C": "📊 Average - Mixed signals, requires monitoring",
            "D": "📉 Below Average - Multiple risk factors"
        }
        
        msg += f"**⭐ OVERALL GRADE: {project.grade_letter}**\n"
        msg += f"{grade_desc.get(project.grade_letter, '')}\n"
        if project.last_graded:
            msg += f"_Last updated: {project.last_graded.strftime('%b %d, %Y')}_\n"
    
    msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # === SOURCES ===
    msg += "**📚 DATA SOURCES**\n"
    if project.data_sources:
        for source in project.data_sources.get("sources", []):
            msg += f"• {source}\n"
    else:
        msg += "• CryptoRank\n• CoinGecko\n• GitHub\n• Twitter\n"
    
    msg += f"\n_Last updated: {project.last_updated.strftime('%b %d, %Y %H:%M UTC')}_"
    
    return msg


def format_stats(stats: Dict[str, Any], sector_breakdown: Dict[str, int], days: int) -> str:
    """Format funding statistics."""
    msg = f"📊 **FUNDING STATISTICS (Last {days} days)**\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    msg += f"**Total Rounds:** {stats['total_rounds']}\n"
    msg += f"**Total Raised:** ${stats['total_raised']:.1f}M\n"
    msg += f"**Avg Round Size:** ${stats['avg_round_size']:.1f}M\n\n"
    
    # Largest round
    if stats['largest_round']:
        largest = stats['largest_round']
        msg += f"**Largest Round:**\n"
        msg += f"  {largest.project.name} · ${largest.amount_raised:.1f}M\n\n"
    
    # By round type
    msg += "**By Round Type:**\n"
    for round_type, data in stats['by_round_type'].items():
        if data['count'] > 0:
            msg += f"• {round_type.replace('_', ' ').title()}: {data['count']} rounds (${data['total']:.1f}M)\n"
    
    msg += "\n━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Sector breakdown
    msg += "**Top Sectors:**\n"
    for sector, count in list(sector_breakdown.items())[:5]:
        if sector:
            msg += f"• {sector}: {count} projects\n"
    
    return msg


def truncate_text(text: str, max_length: int = 4000) -> str:
    """Truncate text to fit Telegram message limits."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 50] + "\n\n_... Report truncated. Full data available via API._"
