import os

from pathlib import Path

BasePath = Path(__file__).resolve().parent.parent.parent

# 마이그레이션 파일 저장 경로
Versions = os.path.join(BasePath, '{{cookiecutter.project_name}}', 'db', 'migrations', 'versions')

# 로그 파일 경로
LogPath = os.path.join(BasePath, 'log')

# Static Path
StaticPath = os.path.join(BasePath, '{{cookiecutter.project_name}}', 'static')
