from enum import Enum
from typing import Any


class CustomCode(Enum):
    """
    사용자 지정 오류 코드
    """

    CAPTCHA_ERROR = (40001, '캡차 오류')

    @property
    def code(self) -> Any:
        """
        오류 코드 가져오기
        """
        return self.value[0]

    @property
    def msg(self) -> Any:
        """
        오류 코드 정보 얻기
        """
        return self.value[1]
