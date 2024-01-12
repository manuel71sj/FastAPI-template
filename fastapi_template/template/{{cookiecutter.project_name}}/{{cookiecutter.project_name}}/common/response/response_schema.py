from typing import Any

from asgiref.sync import sync_to_async
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

_ExcludeData = set[int | str] | dict[int | str, Any] | None
# _ExcludeData = set[int], set[str], dict[int, Any], dict[str, Any] | None

__all__ = ['ResponseModel', 'response_base']


class ResponseModel(BaseModel):
    """
    Uniform Response Model(URM)

    .. tip::
        응답베이스에서 사용자 정의 인코더를 사용하지 안을 때
        이 모델을 사용하면 반환된 데이터가 자동으로 파싱되어
        fastapi 내부의 인코더에 의해 직접 반환됩니다.

    E.g. ::
        @router.get('/test', response_model=ResponseModel)
        def test():
            return ResponseModel(data={'test': 'test'})

        @router.get('/test')
        def test() -> ResponseModel:
            return ResponseModel(data={'test': 'test'})
    """

    # model_config = ConfigDict(
    #   json_encoders={
    #       datetime: lambda x: x.strftime(settings.DATETIME_FORMAT)
    #   }
    # )

    code: int = 200
    msg: str = 'Success'
    data: Any | None = None


class ResponseBase:
    """
    Uniform Response Base(URB)

    .. tip::
        이 클래스의 반환 메서드는 사용자 정의 인코더에 의해 사전 구문 분석된 다음
        fastapi의 내부 인코더에 의해 처리되어 다시 반환되며,
        개인 취향에 따라 성능 손실이 발생할 수 있습니다.

    E.g. ::
        @router.get('/test')
        def test():
            return await response_base.success(data={'test': 'test'})
    """

    @staticmethod
    @sync_to_async
    def __json_encoder(data: Any, exclude: _ExcludeData | None = None, **kwargs: Any) -> Any:
        result = jsonable_encoder(data, exclude=exclude, **kwargs)  # type: ignore
        return result

    async def success(
        self,
        *,
        code: int = 200,
        msg: str = 'Success',
        data: Any | None = None,
        exclude: _ExcludeData | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        요청 성공 반환 일반 메서드

        :param code: 반환 상태 코드
        :param msg: 반품 정보
        :param data: 데이터 반환
        :param exclude: 반환 데이터 필드를 제외합니다.
        :return:
        """
        data = data if data is None else await self.__json_encoder(data, exclude, **kwargs)
        return {'code': code, 'msg': msg, 'data': data}

    async def fail(
        self,
        *,
        code: int = 400,
        msg: str = 'Bad Request',
        data: Any | None = None,
        exclude: _ExcludeData | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        data = data if data is None else await self.__json_encoder(data, exclude, **kwargs)
        
        return {'code': code, 'msg': msg, 'data': data}


response_base = ResponseBase()
