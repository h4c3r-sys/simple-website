from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from bot.database import Base

class GuildSettings(Base):
    """
    Stores per-guild configuration, such as the channel ID where logs should be sent.
    """
    __tablename__ = "guild_settings"

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, unique=True, index=True, nullable=False)
    log_channel_id = Column(BigInteger, nullable=True)

    # Store settings for auto-ban behavior if needed
    auto_ban_enabled = Column(Boolean, default=True)

class BannedWord(Base):
    """
    Stores the actual list of prohibited words for each guild.
    The on_message listener checks against this table.
    """
    __tablename__ = "banned_words"
    __table_args__ = (UniqueConstraint('guild_id', 'word', name='_guild_word_uc'),)

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    word = Column(String, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Optional: track who added it or if it was auto-detected
    source = Column(String, default="auto") # "auto" or "manual"

class StoredMessage(Base):
    """
    Archive of messages scanned from the server.
    These are used as the dataset for the Machine Learning analysis.
    """
    __tablename__ = "stored_messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(BigInteger, unique=True, index=True)
    guild_id = Column(BigInteger, index=True)
    channel_id = Column(BigInteger)
    author_id = Column(BigInteger)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True))
    is_bot = Column(Boolean, default=False)

    # Flags to help training
    is_spam = Column(Boolean, nullable=True) # Null = unknown, True = spam, False = ham
    has_link = Column(Boolean, default=False)
