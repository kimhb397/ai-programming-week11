from pathlib import Path

import pytest

from load_scores import load_scores


@pytest.mark.parametrize("as_string", [False, True])
def test_정상_이름과_점수의_공백을_제거하고_순서와_중복을_보존한다(
    tmp_path, as_string
):
    path = tmp_path / "scores.csv"
    path.write_text(
        "name,score\n"
        "  홍길동  , 0 \n"
        "만점,100\n"
        "홍길동, 80\n"
        '"이,름", 85 \n',
        encoding="utf-8",
    )

    kept, skipped = load_scores(str(path) if as_string else path)

    assert kept == [
        ("홍길동", 0),
        ("만점", 100),
        ("홍길동", 80),
        ("이,름", 85),
    ]
    assert skipped == []


@pytest.mark.parametrize("contents", ["", "name,score\n"])
def test_빈_파일이나_헤더만_있는_파일은_빈_결과를_반환한다(
    tmp_path, contents
):
    path = tmp_path / "empty.csv"
    path.write_text(contents, encoding="utf-8")

    assert load_scores(path) == ([], [])


@pytest.mark.parametrize("as_string", [False, True])
def test_파일이_없으면_FileNotFoundError를_발생시킨다(tmp_path, as_string):
    path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(str(path) if as_string else path)


def test_잘못된_행을_사유와_줄번호를_기록하고_계속_처리한다(tmp_path):
    path = tmp_path / "mixed.csv"
    path.write_text(
        "name,score\n"
        "첫째,10\n"
        "\n"
        "둘째,20\n"
        "열하나\n"
        "열셋,1,추가\n"
        "   ,90\n"
        "이름,   \n"
        "이름,abc\n"
        "이름,-1\n"
        "이름,101\n"
        "셋째,30\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(path)

    assert kept == [("첫째", 10), ("둘째", 20), ("셋째", 30)]
    assert skipped == [
        (5, "열하나", "열 개수가 2가 아님"),
        (6, "열셋,1,추가", "열 개수가 2가 아님"),
        (7, "   ,90", "이름이 비어 있음"),
        (8, "이름,   ", "점수가 비어 있음"),
        (9, "이름,abc", "점수가 정수가 아님"),
        (10, "이름,-1", "점수가 0~100 밖"),
        (11, "이름,101", "점수가 0~100 밖"),
    ]


def test_UTF8_BOM이_있는_파일을_읽는다(tmp_path):
    path = tmp_path / "bom.csv"
    path.write_bytes("\ufeffname,score\n보람,75\n".encode("utf-8"))

    assert load_scores(path) == ([("보람", 75)], [])