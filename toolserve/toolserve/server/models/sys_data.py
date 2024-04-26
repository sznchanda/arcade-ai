
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from toolserve.server.models.base import Base, id_key


class Data(Base):

    __tablename__ = 'sys_data'

    id: Mapped[id_key] = mapped_column(init=False)
    file_name: Mapped[str] = mapped_column(String(255), comment='File name')
    file_path: Mapped[str] = mapped_column(String(255), comment='File path')
