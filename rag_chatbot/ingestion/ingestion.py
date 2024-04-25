from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.core.schema import BaseNode
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline
from dotenv import load_dotenv
from typing import Any, List
from llama_index.core.schema import TransformComponent
from ..setting import IngestionSettings


class ExludeMetadata(TransformComponent):
    def __call__(self, nodes: List[BaseNode], **kwargs: Any) -> List[BaseNode]:
        for node in nodes:
            node.excluded_embed_metadata_keys = ["doc_id"]
            node.excluded_llm_metadata_keys = [
                "file_name", "doc_id", "page_label", "file_path",
                "file_type", "file_size", "creation_date", "last_modified_date"
            ]
        return nodes


load_dotenv()


class LocalDataIngestion:
    def __init__(self, setting: IngestionSettings | None = None) -> None:
        self._setting = setting or IngestionSettings()

    def get_nodes_from_file(
        self,
        input_dir: str = None,
        input_files: list = None
    ) -> List[BaseNode]:
        documents = SimpleDirectoryReader(
            input_dir=input_dir,
            input_files=input_files,
            filename_as_id=True
        ).load_data(show_progress=True)

        splitter = SentenceSplitter.from_defaults(
            chunk_size=self._setting.chunk_size,
            chunk_overlap=self._setting.chunk_overlap,
            paragraph_separator=self._setting.paragraph_sep,
            secondary_chunking_regex=self._setting.chunking_regex
        )
        pipeline = IngestionPipeline(
            transformations=[
                splitter,
                ExludeMetadata(),
                Settings.embed_model
            ]
        )
        return pipeline.run(
            documents=documents,
            show_progress=True,
            num_workers=self._setting.num_workers
        )