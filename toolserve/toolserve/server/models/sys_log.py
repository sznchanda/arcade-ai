

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from toolserve.server.models.base import Base, id_key


class Log(Base):

    __tablename__ = 'sys_log'

    id: Mapped[id_key] = mapped_column(init=False)
    level: Mapped[str] = mapped_column(String(50), comment='Log level')
    msg: Mapped[str] = mapped_column(String(500), comment='Log message')
