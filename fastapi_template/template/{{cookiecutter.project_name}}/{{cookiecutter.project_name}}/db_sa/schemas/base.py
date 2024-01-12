# 사용자 지정 유효성 검사 오류 메시지에 유효성 검사 예상 콘텐츠가 포함되어 있지 않습니다.
# 예상 콘텐츠를 추가하려면 사용자 지정 오류 메시지에 {xxx(예상 콘텐츠 필드)}를 추가하고,
# 예상 콘텐츠 필드는 다음 링크를 참조하세요 # .
# https://github.com/pydantic/pydantic-core/blob/a5cb7382643415b716b1a7a5392914e50f726528/tests/test_errors.py#L266
# 예상 콘텐츠 필드를 바꾸려면 다음 링크를 참조하세요.
# https://github.com/pydantic/pydantic/blob/caa78016433ec9b16a973f92f187a7b6bfde6cb5/docs/errors/errors.md?plain=1#L232
from asgiref.sync import sync_to_async
from fastapi.exceptions import ValidationException
from pydantic import BaseModel, ConfigDict, PydanticUserError, ValidationError
from pydantic_core import ErrorDetails

CUSTOM_VALIDATION_ERROR_MESSAGES: dict[str, str] = {
    'arguments_type': '매개 변수 유형 입력 오류',
    'assertion_error': '어설션 실행 오류',
    'bool_parsing': '부울 입력 구문 분석 오류',
    'bool_type': '부울 값 유형 입력 오류',
    'bytes_too_long': '너무 긴 바이트 길이 입력',
    'bytes_too_short': '바이트 길이 입력이 너무 짧음',
    'bytes_type': '바이트 유형 입력 오류',
    'callable_type': '호출 가능한 객체 유형 입력 오류',
    'dataclass_exact_type': '데이터 클래스 인스턴스 유형 입력 오류',
    'dataclass_type': '데이터 클래스 유형 입력 오류',
    'date_from_datetime_inexact': '날짜 구성 요소 입력이 0이 아닌 경우',
    'date_from_datetime_parsing': '날짜 입력 구문 분석 오류',
    'date_future': '날짜 입력 비미래시제',
    'date_parsing': '날짜 입력 유효성 검사 오류',
    'date_past': '과거형이 아닌 시제로 입력한 날짜',
    'date_type': '날짜 유형 입력 오류',
    'datetime_future': '날짜 시간 입력 비미래 시간',
    'datetime_object_invalid': '잘못된 날짜 및 시간 입력 개체',
    'datetime_parsing': '날짜 및 시간 입력 구문 분석 오류',
    'datetime_past': '날짜 시간 입력 비 과거 시간',
    'datetime_type': '날짜 시간 유형 입력 오류',
    'decimal_max_digits': '소수점 이하 자릿수 초과 입력',
    'decimal_max_places': '소수점 입력 오류',
    'decimal_parsing': '십진수 입력 구문 분석 오류',
    'decimal_type': '소수점 유형 입력 오류',
    'decimal_whole_digits': '소수점 입력 오류',
    'dict_type': '사전 유형 입력 오류',
    'enum': '열거형 멤버 입력 오류, 허용：{expected}',
    'extra_forbidden': '추가 필드 입력 금지',
    'finite_number': '유한 값 입력 오류',
    'float_parsing': '부동 소수점 입력 구문 분석 오류',
    'float_type': '부동 소수점 유형 입력 오류',
    'frozen_field': '필드 입력 오류 정지',
    'frozen_instance': '인스턴스를 동결하여 수정 금지하기',
    'frozen_set_type': '동결 유형 금지 입력',
    'get_attribute_error': '속성 가져오기 오류',
    'greater_than': '입력 값이 너무 큼',
    'greater_than_equal': '입력이 너무 크거나 같음',
    'int_from_float': '정수 유형 입력 오류',
    'int_parsing': '정수 입력 구문 분석 오류',
    'int_parsing_size': '정수 입력 구문 분석 길이 오류',
    'int_type': '정수 유형 입력 오류',
    'invalid_key': '잘못된 키 값을 입력합니다.',
    'is_instance_of': '유형 인스턴스 입력 오류',
    'is_subclass_of': '유형 서브클래스 입력 오류',
    'iterable_type': '이터러블 유형 입력 오류',
    'iteration_error': '반복 값 입력 오류',
    'json_invalid': 'JSON 문자열 입력 오류',
    'json_type': 'JSON 유형 입력 오류',
    'less_than': '입력 값이 너무 작음',
    'less_than_equal': '입력이 너무 작거나 같음',
    'list_type': '목록 유형 입력 오류',
    'literal_error': '문자 값 입력 오류',
    'mapping_type': '매핑 유형 입력 오류',
    'missing': '누락된 필수 필드',
    'missing_argument': '누락된 매개 변수',
    'missing_keyword_only_argument': '누락된 키워드 매개변수',
    'missing_positional_only_argument': '누락된 위치 매개변수',
    'model_attributes_type': '모델 속성 유형 입력 오류',
    'model_type': '모델 인스턴스 입력 오류',
    'multiple_argument_values': '매개변수 값의 과도한 입력',
    'multiple_of': '입력 값은 배수가 아닙니다.',
    'no_such_attribute': '잘못된 속성 값 할당하기',
    'none_required': '입력 값은 다음과 같아야 합니다. None',
    'recursion_loop': '입력 루프 할당',
    'set_type': '컬렉션 유형 입력 오류',
    'string_pattern_mismatch': '문자열 제약 조건 패턴 입력 불일치',
    'string_sub_type': '문자열 하위 유형(엄격 인스턴스가 아님) 입력 오류',
    'string_too_long': '너무 긴 문자열 입력',
    'string_too_short': '문자열 입력이 너무 짧음',
    'string_type': '문자열 유형 입력 오류',
    'string_unicode': '유니코드가 아닌 문자열 입력',
    'time_delta_parsing': '시차 입력 구문 분석 오류',
    'time_delta_type': '시차 유형 입력 오류',
    'time_parsing': '시간 입력 구문 분석 오류',
    'time_type': '시간 유형 입력 오류',
    'timezone_aware': '시간대 입력 정보가 누락되었습니다.',
    'timezone_naive': '시간대 입력 정보 비활성화',
    'too_long': '너무 긴 입력',
    'too_short': '입력이 너무 짧음',
    'tuple_type': '튜플 유형 입력 오류',
    'unexpected_keyword_argument': '예상치 못한 키워드 매개변수 입력',
    'unexpected_positional_argument': '우발적 위치 매개변수 입력',
    'union_tag_invalid': '조인트 유형 리터럴 값 입력 오류',
    'union_tag_not_found': '조인트 유형 매개변수 입력을 찾을 수 없습니다.',
    'url_parsing': 'URL 입력 해상도 오류',
    'url_scheme': 'URL 입력 체계 오류',
    'url_syntax_violation': 'URL 입력 구문 오류',
    'url_too_long': 'URL 입력이 너무 깁니다.',
    'url_type': 'URL 유형 입력 오류',
    'uuid_parsing': 'UUID 입력 구문 분석 오류',
    'uuid_type': 'UUID 유형 입력 오류',
    'uuid_version': 'UUID 버전 유형 입력 오류',
    'value_error': '값 입력 오류',
}

CUSTOM_USAGE_ERROR_MESSAGES: dict[str, str] = {
    'class-not-fully-defined': '클래스 속성 유형이 완전히 정의되지 않음',
    'custom-json-schema': '__modify_schema__ 메서드는 V2에서 더 이상 사용되지 않습니다.',
    'decorator-missing-field': '잘못된 필드 유효성 검사기가 정의되었습니다.',
    'discriminator-no-field': '판별자 필드가 모두 정의되지 않음',
    'discriminator-alias-type': '식별자 필드는 문자열이 아닌 유형을 사용하여 정의됩니다.',
    'discriminator-needs-literal': '판별자 필드는 리터럴 값을 사용하여 정의해야 합니다.',
    'discriminator-alias': '식별자 필드 별칭의 일관성 없는 정의',
    'discriminator-validator': '판별자 필드 금지 정의 필드 유효성 검사기',
    'model-field-overridden': '입력되지 않은 필드의 덮어쓰기는 금지됩니다.',
    'model-field-missing-annotation': '누락된 필드 유형 정의',
    'config-both': '구성 항목의 반복 정의',
    'removed-kwargs': '제거된 키워드 구성 매개변수 호출',
    'invalid-for-json-schema': '잘못된 JSON 유형이 있습니다.',
    'base-model-instantiated': '기본 모델의 인스턴스화 금지',
    'undefined-annotation': '누락된 유형 정의',
    'schema-for-unknown-type': '알 수 없는 유형 정의',
    'create-model-field-definitions': '필드 정의 오류',
    'create-model-config-base': '구성 항목 정의 오류',
    'validator-no-fields': '필드 유효성 검사기에 의해 지정되지 않은 필드',
    'validator-invalid-fields': '필드 유효성 검사기 필드 정의 오류',
    'validator-instance-method': '필드 유효성 검사기는 클래스 메서드여야 합니다.',
    'model-serializer-instance-method': 'Serialiser는 인스턴스 메서드여야 합니다.',
    'validator-v1-signature': 'V1 필드 유효성 검사기 오류 사용 중단',
    'validator-signature': '필드 유효성 검사기 서명 오류',
    'field-serializer-signature': '필드 시리얼라이저 서명이 인식되지 않음',
    'model-serializer-signature': '모델 시리얼라이저 서명이 인식되지 않음',
    'multiple-field-serializers': '필드 직렬화기 중복 정의',
    'invalid_annotated_type': '잘못된 유형 정의',
    'type-adapter-config-unused': '유형 어댑터 구성 항목 정의 오류',
    'root-model-extra': '루트 모델에서는 추가 필드 정의를 금지합니다.',
}


@sync_to_async
def convert_validation_errors(
    e: ValidationError | ValidationException, custom_messages: dict[str, str]
) -> list[ErrorDetails]:
    new_errors: list[ErrorDetails] = []

    for error in e.errors():
        custom_message = custom_messages.get(error['type'])

        if custom_message:
            ctx = error.get('ctx')
            error['msg'] = custom_message.format(**ctx) if ctx else custom_message

        new_errors.append(error)

    return new_errors


@sync_to_async
def convert_usage_errors(e: PydanticUserError, custom_messages: dict[str, str]) -> str:
    custom_message = custom_messages.get(str(e.code))

    if custom_message:
        return custom_message

    return e.message


class SchemaBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
