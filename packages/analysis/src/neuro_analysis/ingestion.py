from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
import re

from pydantic import BaseModel, Field

from neuro_core import ArtifactLineage, ContentAsset, ContentSegment


@dataclass
class IngestionError(Exception):
    code: str
    message: str
    status_code: int

    def __str__(self) -> str:
        return self.message


class TextIngestionRequest(BaseModel):
    project_id: str
    content_type: str
    body: str
    title: str | None = None
    source_kind: str = "user_input"


class TextIngestionResult(BaseModel):
    asset: ContentAsset
    segments: list[ContentSegment]


class IngestionService:
    sentence_pattern = re.compile(r"[^.!?]+[.!?]|[^.!?]+$", re.MULTILINE)

    def ingest_text(self, request: TextIngestionRequest) -> TextIngestionResult:
        normalized_body = self._normalize_body(request.body)
        if not normalized_body:
            raise IngestionError(
                code="content_empty",
                message="Input body is empty after normalization",
                status_code=422,
            )

        asset_id = self._stable_id("asset", request.project_id, request.content_type, normalized_body)
        asset = ContentAsset(
            asset_id=asset_id,
            project_id=request.project_id,
            content_type=request.content_type,
            body=normalized_body,
            title=request.title,
            source_kind=request.source_kind,  # type: ignore[arg-type]
            lineage=ArtifactLineage(source_project_id=request.project_id),
        )

        segments: list[ContentSegment] = []
        for paragraph_index, paragraph in enumerate(normalized_body.split("\n\n")):
            start_char = normalized_body.find(paragraph, segments[-1].end_char if segments else 0)
            end_char = start_char + len(paragraph)
            paragraph_id = self._stable_id("segment", asset_id, "paragraph", paragraph_index, start_char, end_char)
            segments.append(
                ContentSegment(
                    segment_id=paragraph_id,
                    asset_id=asset_id,
                    index=len(segments),
                    kind="paragraph",
                    text=paragraph,
                    start_char=start_char,
                    end_char=end_char,
                    lineage=ArtifactLineage(
                        source_project_id=request.project_id,
                        source_asset_id=asset_id,
                    ),
                )
            )

            for sentence in self.sentence_pattern.finditer(paragraph):
                sentence_text = sentence.group(0).strip()
                if not sentence_text:
                    continue
                sentence_start = start_char + sentence.start()
                sentence_end = sentence_start + len(sentence_text)
                sentence_id = self._stable_id(
                    "segment",
                    asset_id,
                    "sentence",
                    paragraph_index,
                    sentence_start,
                    sentence_end,
                )
                segments.append(
                    ContentSegment(
                        segment_id=sentence_id,
                        asset_id=asset_id,
                        index=len(segments),
                        kind="sentence",
                        text=sentence_text,
                        start_char=sentence_start,
                        end_char=sentence_end,
                        lineage=ArtifactLineage(
                            source_project_id=request.project_id,
                            source_asset_id=asset_id,
                        ),
                    )
                )

        return TextIngestionResult(asset=asset, segments=segments)

    def _normalize_body(self, body: str) -> str:
        lines = [line.strip() for line in body.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
        paragraphs: list[str] = []
        buffer: list[str] = []

        for line in lines:
            if line:
                buffer.append(line)
                continue
            if buffer:
                paragraphs.append(" ".join(buffer))
                buffer = []

        if buffer:
            paragraphs.append(" ".join(buffer))

        return "\n\n".join(paragraphs).strip()

    def _stable_id(self, prefix: str, *parts: object) -> str:
        digest = sha1("::".join(map(str, parts)).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"

