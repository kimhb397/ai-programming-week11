from pathlib import Path

import pytest

from load_scores import load_scores


def test_정상_파일을_읽는다():
    kept, skipped = load_scores(Path(__file__).with_name("scores.csv"))
    assert len(kept) == 5


def test_유효하지_않은_행을_건너뛴다():
    kept, skipped = load_scores(Path(__file__).with_name("scores.csv"))
    assert len(skipped) == 5


def test_없는_파일이면_오류가_난다(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "없는파일.csv")


def test_헤더만_있으면_빈_결과가_나온다():
    kept, skipped = load_scores(Path(__file__).with_name("empty.csv"))
    assert kept == []
    assert skipped == []


@pytest.mark.parametrize("점수, 유효한가", [
    (-1, False),
    (0, True),
    (1, True),
    (99, True),
    (100, True),
    (101, False),
])
def test_점수_경계값(점수, 유효한가, tmp_path):
    path = tmp_path / "임시.csv"
    path.write_text(f"name,score\n테스트,{점수}\n", encoding="utf-8")

    kept, skipped = load_scores(path)
    assert (len(kept) == 1) == 유효한가