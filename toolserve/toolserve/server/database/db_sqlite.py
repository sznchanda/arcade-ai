#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from typing import Annotated
from uuid import uuid4

from fastapi import Depends
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from toolserve.server.common.log import log
from toolserve.server.core.conf import settings
from toolserve.server.models import (
    MappedBase,
    Log,
    Artifact,
    Data,
)


def create_engine_and_session(url: str | URL):
    try:
        engine = create_async_engine(url, echo=settings.DB_ECHO, future=True, pool_pre_ping=True)
    except Exception as e:
        log.error('❌ Error starting db session {}', e)
        sys.exit()
    else:
        db_session = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
        return engine, db_session


SQLALCHEMY_DATABASE_URL = (
    f'sqlite+aiosqlite:///{settings.WORK_DIR}/{settings.DB_DATABASE}.db'
)

async_engine, async_db_session = create_engine_and_session(SQLALCHEMY_DATABASE_URL)


async def get_db() -> AsyncSession:
    """Provide a database session for a single request."""
    session = async_db_session()
    try:
        yield session
    except Exception as se:
        await session.rollback()
        raise se
    finally:
        await session.close()


# Session Annotated
CurrentSession = Annotated[AsyncSession, Depends(get_db)]


async def create_table():
    """Create the database tables if they do not exist."""
    async with async_engine.begin() as conn:
        try:
            await conn.run_sync(MappedBase.metadata.create_all)
        except Exception as e:
            log.error('❌ Error creating tables {}', e)
            raise e


def uuid4_str() -> str:
    """Generate a UUID4 string."""
    return str(uuid4())
