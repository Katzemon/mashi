from sqlalchemy import select

from data.db import db, Mashers


class MashersDao:
    def __init__(self):
        self.session = db.session

    def connect_wallet(self, user_id: int, wallet: str):
        session = self.session()
        try:
            user = session.get(Mashers, user_id)
            if user:
                user.wallet = wallet
            else:
                user = Mashers(userid=user_id, wallet=wallet)
                session.add(user)
            session.commit()
        finally:
            session.close()

    def disconnect_wallet(self, user_id: int):
        session = self.session()
        try:
            user = session.get(Mashers, user_id)
            if user:
                user.wallet = None
                session.commit()
        finally:
            session.close()

    def get_wallet(self, user_id: int) -> str | None:
        session = self.session()
        try:
            user = session.get(Mashers, user_id)
            return user.wallet if user else None
        finally:
            session.close()

    def get_user_by_wallet(self, wallet: str) -> Mashers | None:
        session = self.session()
        try:
            stmt = select(Mashers).where(Mashers.wallet == wallet)
            result = session.execute(stmt).scalar_one_or_none()
            return result
        finally:
            session.close()
