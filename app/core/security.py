from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
	"""Genera un hash bcrypt para una contraseña."""
	password_bytes = password.encode("utf-8")
	return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
	"""Compara una contraseña con su hash bcrypt."""
	try:
		return bcrypt.checkpw(
			password.encode("utf-8"), hashed_password.encode("utf-8")
		)
	except ValueError:
		return False


def create_access_token(user_id: int) -> str:
	"""Crea un JWT de acceso con expiración configurada."""
	expires_at = datetime.now(timezone.utc) + timedelta(
		minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
	)
	return jwt.encode(
		{"sub": str(user_id), "exp": expires_at},
		settings.SECRET_KEY,
		algorithm=settings.ALGORITHM,
	)


def decode_access_token(token: str) -> int | None:
	"""Valida un JWT y devuelve el identificador de usuario."""
	try:
		payload = jwt.decode(
			token,
			settings.SECRET_KEY,
			algorithms=[settings.ALGORITHM],
		)
	except jwt.InvalidTokenError:
		return None

	subject = payload.get("sub")
	if not isinstance(subject, str) or not subject.isdecimal():
		return None
	return int(subject)
