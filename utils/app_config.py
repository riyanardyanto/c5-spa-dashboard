"""Application configuration data structures."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple

from configparser import ConfigParser

CONFIG_FILENAME = "config.ini"


@dataclass(frozen=True)
class AppDataConfig:
    """Immutable container for application configuration values."""

    environment: str
    username: str
    password: str
    link_up: Tuple[str, ...]
    url: str
    verify_ssl: bool = True
    ca_bundle: str | None = None

    @classmethod
    def from_parser(
        cls,
        parser: ConfigParser,
        section: str | None = None,
    ) -> "AppDataConfig":
        """Create an instance from a ``ConfigParser`` object."""

        section_name = section or parser.default_section
        if section_name != parser.default_section and not parser.has_section(
            section_name
        ):
            section_name = parser.default_section

        get = parser.get
        environment = get(section_name, "environment", fallback="development")
        username = get(section_name, "username", fallback="")
        password = get(section_name, "password", fallback="")
        link_up_raw = get(section_name, "link_up", fallback="")
        url = get(section_name, "url", fallback="")
        verify_ssl = parser.getboolean(section_name, "verify_ssl", fallback=True)
        ca_bundle = get(section_name, "ca_bundle", fallback=None) or None

        link_up = cls._normalize_links(link_up_raw)

        return cls(
            environment=environment.strip(),
            username=username.strip(),
            password=password.strip(),
            link_up=link_up,
            url=url.strip(),
            verify_ssl=verify_ssl,
            ca_bundle=ca_bundle,
        )

    @staticmethod
    def _normalize_links(value: str) -> Tuple[str, ...]:
        parts: Iterable[str] = (part.strip() for part in value.split(","))
        return tuple(part for part in parts if part)

    def as_dict(self) -> dict[str, str | Tuple[str, ...]]:
        """Expose configuration as a dictionary."""

        return {
            "environment": self.environment,
            "username": self.username,
            "password": self.password,
            "link_up": self.link_up,
            "url": self.url,
            "verify_ssl": self.verify_ssl,
            "ca_bundle": self.ca_bundle,
        }


def _resolve_base_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(sys.modules["__main__"].__file__).resolve().parent


def get_config_path() -> Path:
    """Return the absolute path to the application configuration file."""

    return _resolve_base_path() / CONFIG_FILENAME


def create_config(path: Path | None = None) -> Path:
    """Create a default configuration file when none exists."""

    config = ConfigParser()
    link_up = ["LU18", "LU21", "LU26", "LU27"]
    config["DEFAULT"] = {
        "environment": "production",
        "username": "",
        "password": "",
        "link_up": ",".join(link_up),
        "url": "https://ots.spappa.aws.private-pmideep.biz/db.aspx?",
        # If you are using self-signed certificates or a private CA,
        # set `verify_ssl` to False or provide `ca_bundle` with a path
        # to a PEM file containing your certificate(s).
        "verify_ssl": "True",
        "ca_bundle": "",
    }

    target_path = path or get_config_path()
    with target_path.open("w", encoding="utf-8") as handle:
        config.write(handle)

    return target_path


def read_config(section: str | None = None) -> AppDataConfig:
    """Load the application configuration data as an ``AppDataConfig``."""

    config_path = get_config_path()
    parser = ConfigParser()

    if not config_path.exists():
        create_config(config_path)

    parser.read(config_path, encoding="utf-8")
    return AppDataConfig.from_parser(parser, section=section)


def get_base_url(section: str | None = None) -> str:
    """Return the configured base URL (convenience wrapper).

    This central helper ensures other modules obtain the base URL from a
    single place and always receive a non-null string.
    """

    cfg = read_config(section=section)
    return cfg.url or ""
