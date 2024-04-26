from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from toolserve.server.models.base import Base, id_key


class Artifact(Base):

    __tablename__ = 'sys_artifact'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(String(255), comment='Artifact name')
    file_path: Mapped[str] = mapped_column(String(255), comment='File path')
