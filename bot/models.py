from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from bot.database import Base

class GuildSettings(Base):
    __tablename__ = "guild_settings"

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, unique=True, index=True, nullable=False)
    log_channel_id = Column(BigInteger, nullable=True)

    # Store settings for auto-ban behavior if needed
    auto_ban_enabled = Column(Boolean, default=True)

class BannedWord(Base):
    __tablename__ = "banned_words"

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    word = Column(String, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Optional: track who added it or if it was auto-detected
    source = Column(String, default="auto") # "auto" or "manual"

class StoredMessage(Base):
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
