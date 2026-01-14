"""
FundFlow Telegram Bot - Main Entry Point
Handles bot initialization and starts the application.
"""
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from loguru import logger

from config.settings import settings
from bot.handlers import (
    start_command,
    help_command,
    find_command,
    pdf_callback_handler,
    search_command,
    latest_command,
    investor_command,
    report_command,
    filter_command,
    watch_command,
    unwatch_command,
    stats_command,
    admin_refresh_command,
    export_command,
    handle_message
)


def setup_logging():
    """Configure logging."""
    logger.add(
        "logs/fundflow_{time}.log",
        rotation="1 day",
        retention="30 days",
        level=settings.log_level
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors in the bot."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Sorry, an error occurred. Please try again later."
        )


async def post_init(application: Application):
    """Initialize resources after bot starts."""
    logger.info("🚀 FundFlow bot initialized")
    
    # Set bot commands menu
    from telegram import BotCommand
    commands = [
        BotCommand("find", "Search, Discover & Generate Dossiers"),
        BotCommand("latest", "Recent Funding Rounds"),
        BotCommand("investor", "Investor Portfolios"),
        BotCommand("stats", "Market Statistics"),
        BotCommand("watch", "Monitor Project"),
        BotCommand("help", "Detailed Help")
    ]
    await application.bot.set_my_commands(commands)
    
    logger.info(f"Environment: {settings.environment}")
    

def main():
    """Main function to run the bot."""
    # Setup
    setup_logging()
    logger.info("Starting FundFlow Telegram Bot...")
    
    # Create application
    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .post_init(post_init)
        .build()
    )
    
    # Register command handlers
    from telegram.ext import CallbackQueryHandler
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("find", find_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("latest", latest_command))
    application.add_handler(CommandHandler("investor", investor_command))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("filter", filter_command))
    application.add_handler(CommandHandler("watch", watch_command))
    application.add_handler(CommandHandler("unwatch", unwatch_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("admin_refresh", admin_refresh_command))
    application.add_handler(CommandHandler("export", export_command))
    
    application.add_handler(CallbackQueryHandler(pdf_callback_handler, pattern="^pdf_"))
    
    # Register message handler for non-command messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("✅ Bot is running. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
