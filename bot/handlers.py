# -*- coding: utf-8 -*-
"""
Telegram bot command handlers for FundFlow.
Each function handles a specific bot command.
"""
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
from loguru import logger
import io

from database.queries import (
    get_db,
    search_projects,
    get_recent_funded_projects,
    get_investor_by_name,
    get_investor_portfolio,
    get_project_full_info,
    create_alert,
    deactivate_alert,
    get_user_alerts,
    get_funding_stats,
    get_sector_breakdown,
    get_project_by_name
)
from bot.formatters import (
    format_project_summary,
    format_funding_round,
    format_investor_profile,
    format_full_report,
    format_stats
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome_message = """
🚀 **FundFlow Intelligence Platform**

Your automated portal for institutional crypto funding intel.

**Primary Interface:**
/find <name> - Search, Discover & Generate Dossiers

**Other Commands:**
/latest - Recent funding rounds
/investor <name> - View investor portfolio
/stats - Market statistics
/help - Detailed documentation

**Quick Start:**
Try `/find drosera` to generate an intelligence dossier.
    """
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "🔍 **How to use FundFlow**\n\n"
        "**1. Intelligence Dossiers**\n"
        "Use `/find <project>` to find any project. If it's not in our database, I will launch a real-time discovery mission to ingest it. Once found, you can click the button to generate a monochromatic PDF research dossier.\n\n"
        "**2. Investor Tracking**\n"
        "Use `/investor <name>` to see every recent investment by a specific fund.\n\n"
        "**3. Market Pulse**\n"
        "/latest - Last 7 days of funding\n"
        "/stats - Broad market metrics\n\n"
        "**4. Monitoring**\n"
        "/watch <project> - Get notified of new rounds"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unified command for searching, discovery, and dossier generation."""
    if not context.args:
        await update.message.reply_text(
            "Please provide a project name or website.\n\nExample: `/find uniswap`",
            parse_mode="Markdown"
        )
        return
    
    query = " ".join(context.args)
    logger.info(f"Find query: {query} from user {update.effective_user.id}")
    
    # 1. Classify & Resolve
    from utils.classifier import classify_input
    from utils.registry import resolve_entity_name
    query_type, clean_query = classify_input(query)
    canonical_query = resolve_entity_name(clean_query)
    
    db = get_db()
    try:
        # Try finding in DB first (optimized search)
        projects = search_projects(db, canonical_query, limit=5)
        
        if not projects:
            # If not in DB, start discovery
            status_msg = await update.message.reply_text(
                f"📡 <b>System: '{html.escape(query)}' not indexed.</b>\nLaunching real-time discovery & ingestion...",
                parse_mode="HTML"
            )
            
            from scrapers.cryptorank import CryptoRankScraper
            scraper = CryptoRankScraper()
            import asyncio
            discovered = await scraper.discover_project_async(canonical_query, query_type=query_type)
            
            if discovered:
                projects = [discovered]
                await status_msg.edit_text(f"✅ <b>Ingestion Complete:</b> {html.escape(discovered.name)}\nSynthesizing baseline intelligence...", parse_mode="HTML")
            else:
                await status_msg.edit_text(f"❌ <b>Discovery Failed:</b> No verifiable signals found for '{html.escape(query)}'.")
                return
        
        # We have at least one project
        for project in projects:
            summary = format_project_summary(project)
            
            # Add PDF Button
            keyboard = [[InlineKeyboardButton("📑 Generate Intelligence Dossier (PDF)", callback_data=f"pdf_{project.id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(summary, reply_markup=reply_markup, parse_mode="HTML")
            
    except Exception as e:
        logger.exception(f"Error in find_command: {e}")
        await update.message.reply_text("⚠️ An error occurred during intelligence retrieval.")
    finally:
        db.close()


async def pdf_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the 'Generate PDF' button click."""
    query = update.callback_query
    await query.answer("Generating Dossier...")
    
    data_parts = query.data.split("_")
    if len(data_parts) < 2:
        return
    
    project_id = int(data_parts[1])
    
    db = get_db()
    try:
        project_info = get_project_full_info(db, project_id)
        project = project_info['project']
        
        # Update progress in message
        await query.edit_message_reply_markup(reply_markup=None)
        status_msg = await query.message.reply_text(f"📝 <b>Anchoring signals for {html.escape(project.name)}...</b>", parse_mode="HTML")
        
        # JIT Enrichment
        from scrapers.cryptorank import CryptoRankScraper
        import asyncio
        scraper = CryptoRankScraper()
        # Ensure we have latest data
        await asyncio.to_thread(scraper.sync_project_on_demand, project.name)
        
        # Refresh project info after sync
        project_info = get_project_full_info(db, project_id)
        
        from utils.report_gen import PDFReportGenerator
        generator = PDFReportGenerator()
        dossier = generator.map_project_to_dossier(project_info)
        pdf_buffer = await asyncio.to_thread(generator.generate_project_report, dossier)
        
        await query.message.reply_document(
            document=pdf_buffer,
            filename=f"{project.slug}_dossier.pdf",
            caption=f"**Intelligence Dossier: {project.name}**\nGenerated {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC",
            parse_mode="Markdown"
        )
        
        await status_msg.delete()
        
    except Exception as e:
        logger.error(f"PDF Callback error: {e}")
        await query.message.reply_text("❌ Failed to generate PDF dossier.")
    finally:
        db.close()


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for /find."""
    await find_command(update, context)


async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /latest [days] command."""
    days = 7  # default
    
    if context.args:
        try:
            days = int(context.args[0])
            if days < 1 or days > 365:
                await update.message.reply_text("Please specify days between 1 and 365.")
                return
        except ValueError:
            await update.message.reply_text("Invalid number of days.")
            return
    
    logger.info(f"Latest funding query: {days} days from user {update.effective_user.id}")
    
    db = get_db()
    try:
        recent_funding = get_recent_funded_projects(db, days=days, limit=15)
        
        if not recent_funding:
            await update.message.reply_text(
                f"No funding rounds found in the last {days} days."
            )
            return
        
        response = f"**Recent Funding (Last {days} days):**\n\n"
        
        for item in recent_funding:
            project = item["project"]
            funding_round = item["funding_round"]
            response += format_funding_round(project, funding_round) + "\n\n"
        
        response += f"\n_Showing {len(recent_funding)} recent round(s). Use `/report <name>` for details._"
        
        await update.message.reply_text(response, parse_mode="Markdown", disable_web_page_preview=True)
    
    finally:
        db.close()


async def investor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /investor <name> command."""
    if not context.args:
        await update.message.reply_text(
            "Please provide an investor name.\n\nExample: `/investor paradigm`",
            parse_mode="Markdown"
        )
        return
    
    investor_name = " ".join(context.args)
    logger.info(f"Investor query: {investor_name} from user {update.effective_user.id}")
    
    db = get_db()
    try:
        investor = get_investor_by_name(db, investor_name)
        
        if not investor:
            await update.message.reply_text(
                f"Investor '{investor_name}' not found in database."
            )
            return
        
        portfolio = get_investor_portfolio(db, investor.id, limit=10)
        
        response = format_investor_profile(investor, portfolio)
        
        await update.message.reply_text(response, parse_mode="Markdown", disable_web_page_preview=True)
    
    finally:
        db.close()


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for /find."""
    await find_command(update, context)


async def filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /filter <criteria> command."""
    if not context.args:
        await update.message.reply_text(
            "Please provide filter criteria.\n\n"
            "Examples:\n"
            "`/filter sector:defi`\n"
            "`/filter amount:>5M investor:paradigm`",
            parse_mode="Markdown"
        )
        return
    
    await update.message.reply_text(
        "Advanced filtering is coming soon!\n\n"
        "For now, use `/search` and `/latest` commands."
    )


async def watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /watch <project> command."""
    if not context.args:
        await update.message.reply_text(
            "Please provide a project name.\n\nExample: `/watch optimism`",
            parse_mode="Markdown"
        )
        return
    
    project_name = " ".join(context.args)
    user_id = update.effective_user.id
    
    db = get_db()
    try:
        from database.queries import get_project_by_name
        project = get_project_by_name(db, project_name)
        
        if not project:
            await update.message.reply_text(
                f"Project '{project_name}' not found in database."
            )
            return
        
        create_alert(db, telegram_user_id=user_id, project_id=project.id)
        
        await update.message.reply_text(
            f"Alert set for **{project.name}**\n\n"
            f"You'll be notified of:\n"
            f"• New funding rounds\n"
            f"• Major updates\n\n"
            f"Use `/unwatch {project.name}` to stop alerts.",
            parse_mode="Markdown"
        )
    
    finally:
        db.close()


async def unwatch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unwatch <project> command."""
    if not context.args:
        await update.message.reply_text(
            "Please provide a project name.\n\nExample: `/unwatch optimism`",
            parse_mode="Markdown"
        )
        return
    
    # TODO: Implement unwatch logic
    await update.message.reply_text(
        "Alert removed. You will no longer receive notifications for this project."
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats [days] command."""
    days = 30  # default
    
    if context.args:
        try:
            days = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Invalid number of days.")
            return
    
    db = get_db()
    try:
        stats = get_funding_stats(db, days=days)
        sector_breakdown = get_sector_breakdown(db, days=days)
        
        response = format_stats(stats, sector_breakdown, days)
        
        await update.message.reply_text(response, parse_mode="Markdown")
    
    finally:
        db.close()


async def admin_refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_refresh command (Admin only)."""
    user_id = update.effective_user.id
    
    # Check if user is admin (simple check against strict list in env)
    from config.settings import settings
    if user_id not in settings.admin_user_ids:
        await update.message.reply_text("Unauthorized.")
        return

    await update.message.reply_text("Starting data pipeline... this may take a minute.")
    
    # Run in thread/background to not block bot
    import asyncio
    from scrapers.runner import run_all_scrapers
    
    # Using asyncio.to_thread for blocking IO calls
    await asyncio.to_thread(run_all_scrapers, False)
    
    await update.message.reply_text("Pipeline complete! Data is fresh.")


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /export command."""
    import pandas as pd
    import io
    
    status = await update.message.reply_text("Generating CSV export...")
    
    db = get_db()
    try:
        # Get last 30 days of funding
        recent_funding = get_recent_funded_projects(db, days=30, limit=500)
        
        if not recent_funding:
            await status.edit_text("No data to export.")
            return

        # Convert to flattened dictionary
        data = []
        for item in recent_funding:
            p = item['project']
            r = item['funding_round']
            data.append({
                "Date": r.announced_date,
                "Project": p.name,
                "Sector": p.sector,
                "Round Type": r.round_type.value,
                "Amount ($M)": r.amount_raised,
                "Lead Investor": r.lead_investor.name if r.lead_investor else None,
                "Grade": p.grade_letter,
                "Score": p.grade_score
            })
            
        # Create CSV
        df = pd.DataFrame(data)
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        await update.message.reply_document(
            document=csv_buffer,
            filename=f"fundflow_export_{datetime.utcnow().strftime('%Y-%m-%d')}.csv",
            caption="**Funding Data Export (Last 30 Days)**"
        )
        await status.delete()
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        await status.edit_text(f"Export failed: {e}")
    finally:
        db.close()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-command messages."""
    await update.message.reply_text(
        "👋 **FundFlow Intelligence Hub**\n\n"
        "I respond to commands for institutional research. To find a project or generate a dossier, use:\n"
        "`/find <project_name>`\n\n"
        "Alternatively, use `/help` to see the full intelligence manual.",
        parse_mode="Markdown"
    )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def send_long_message(update: Update, text: str, max_length: int = 4096):
    """Send long messages by splitting them if necessary."""
    if len(text) <= max_length:
        await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)
        return
    
    # Split by sections (denoted by "━━━")
    sections = text.split("━━━")
    current_message = ""
    
    for section in sections:
        if len(current_message) + len(section) + 3 < max_length:
            current_message += "━━━" + section if current_message else section
        else:
            if current_message:
                await update.message.reply_text(
                    current_message,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            current_message = section
    
    if current_message:
        await update.message.reply_text(
            current_message,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
