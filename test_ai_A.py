from pathlib import Path

import pytest

from load_scores import load_scores


def _write_csv(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "scores.csv"
    path.write_text(content, encoding="utf-8")
    return path


def test_유효한_점수와_중복_이름을_모두_보존한다(tmp_path):
    path = _write_csv(
        tmp_path,
        "name,score\n"
        " 김하나 , 0 \n"
        "김하나,100\n",
    )

    kept, skipped = load_scores(path)

    assert kept == [("김하나", 0), ("김하나", 100)]
    assert skipped == []


def test_헤더만_있는_파일은_빈_결과를_반환한다(tmp_path):
    path = _write_csv(tmp_path, "name,score\n")

    assert load_scores(path) == ([], [])


def test_빈_파일은_빈_결과를_반환한다(tmp_path):
    path = _write_csv(tmp_path, "")

    assert load_scores(path) == ([], [])


def test_없는_파일이면_filenotfounderror를_그대로_발생시킨다(tmp_path):
    path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(path)


@pytest.mark.parametrize(
    ("row", "reason"),
    [
        ("한칸", "열 개수가 2가 아님"),
        ("세칸,80,추가", "열 개수가 2가 아님"),
        (",90", "이름이 비어 있음"),
        ("이름,", "점수가 비어 있음"),
        ("이름,결석", "점수가 정수가 아님"),
        ("이름,88.5", "점수가 정수가 아님"),
        ("이름,-1", "점수가 0~100 밖"),
        ("이름,101", "점수가 0~100 밖"),
    ],
)
def test_유효하지_않은_행을_사유와_줄번호를_기록하고_건너뛴다(
    tmp_path, row, reason
):
    path = _write_csv(tmp_path, f"name,score\n{row}\n")

    kept, skipped = load_scores(path)

    assert kept == []
    assert skipped == [(2, row, reason)]


@pytest.mark.parametrize(
    ("score", "expected_kept"),
    [
        ("0", [("테스트", 0)]),
        ("100", [("테스트", 100)]),
        ("-1", []),
        ("101", []),
    ],
)
def test_점수_범위의_경계값을_검사한다(tmp_path, score, expected_kept):
    path = _write_csv(tmp_path, f"name,score\n테스트,{score}\n")

    kept, skipped = load_scores(path)

    assert kept == expected_kept
    assert len(skipped) == (0 if expected_kept else 1)


def test_빈_줄은_기록하지_않고_줄번호는_유지한다(tmp_path):
    path = _write_csv(tmp_path, "name,score\n\n이름,잘못됨\n")

    kept, skipped = load_scores(path)

    assert kept == []
    assert skipped == [(3, "이름,잘못됨", "점수가 정수가 아님")]


def test_utf8_bom이_있는_csv도_읽는다(tmp_path):
    path = tmp_path / "scores.csv"
    path.write_text("name,score\n이름,75\n", encoding="utf-8-sig")

    assert load_scores(path) == ([("이름", 75)], [])