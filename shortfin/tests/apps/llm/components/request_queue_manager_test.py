# Copyright 2025 Advanced Micro Devices, Inc.
#
# Licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import shortfin.array as sfnp
from shortfin_apps.llm.components.config_struct import ModelParams, PagedKVCacheParams
from shortfin_apps.llm.components.token_selection_strategy.config import DecodeConfig
from shortfin_apps.llm.components.request_queue_manager import RequestQueueManager
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def encoding_4():
    mock_encoding = MagicMock()
    mock_encoding.ids.return_value = [1, 2, 3, 4]
    return mock_encoding


@pytest.fixture
def encoding_2():
    mock_encoding = MagicMock()
    mock_encoding.ids.return_value = [1, 2]
    return mock_encoding


@pytest.fixture
def model_params():
    return ModelParams(
        max_seq_len=512,
        transformer_block_count=42,
        attn_head_dim=42,
        prefill_batch_sizes=[4],
        decode_batch_sizes=[2],
        top_k=5,
        paged_kv_cache=PagedKVCacheParams(
            block_seq_stride=2,
            attention_head_count_kv=42,
            device_block_count=100,
            kv_cache_dtype=sfnp.float16,
        ),
    )


@pytest.fixture
def responder():
    return MagicMock()


@pytest.fixture
def manager(model_params):
    return RequestQueueManager(
        model_params=model_params,
        max_queue_size=3,
    )


def test_add_to_queue_success(manager, responder, encoding_4):
    decode_config = DecodeConfig(
        num_beams=1, top_k=5, use_beam_search=False, max_completion_tokens=10
    )
    request_id = manager.add_to_queue(
        decode_configs=[decode_config],
        input_batch=[encoding_4],
        is_pretokenized=True,
        responder=responder,
    )
    assert request_id is not None
    assert manager.available_page_count < 100


def test_add_to_queue_full(manager, responder, encoding_2):
    manager._current_queue_size = 3
    decode_config = DecodeConfig(
        num_beams=1, top_k=5, use_beam_search=False, max_completion_tokens=10
    )
    request_id = manager.add_to_queue(
        decode_configs=[decode_config],
        input_batch=[encoding_2],
        is_pretokenized=True,
        responder=responder,
    )
    assert request_id is None
    responder.send_error.assert_called_once()


def test_add_to_queue_topk_mismatch(manager, responder, encoding_2):
    manager.model_params.top_k = 2
    decode_config = DecodeConfig(
        num_beams=1, top_k=5, use_beam_search=False, max_completion_tokens=10
    )
    request_id = manager.add_to_queue(
        decode_configs=[decode_config],
        input_batch=[encoding_2],
        is_pretokenized=True,
        responder=responder,
    )
    assert request_id is None
    responder.send_error.assert_called_once()


def test_add_to_queue_memory_fail(manager, responder, encoding_4):
    manager.available_page_count = 1  # Force failure
    decode_config = DecodeConfig(
        num_beams=1, top_k=5, use_beam_search=False, max_completion_tokens=100
    )
    request_id = manager.add_to_queue(
        decode_configs=[decode_config],
        input_batch=[encoding_4],
        is_pretokenized=True,
        responder=responder,
    )
    assert request_id is None
    responder.send_error.assert_called_once()


def test_remove_from_queue_success(manager, encoding_2, responder):
    decode_config = DecodeConfig(
        num_beams=1, top_k=5, use_beam_search=False, max_completion_tokens=10
    )
    request_id = manager.add_to_queue(
        decode_configs=[decode_config],
        input_batch=[encoding_2],
        is_pretokenized=True,
        responder=responder,
    )
    used_pages = manager._request_pages[request_id]
    available_before = manager.available_page_count

    manager.remove_from_queue(request_id)

    assert request_id not in manager._current_tasks
    assert request_id not in manager._request_pages
    assert manager.available_page_count == available_before + used_pages


def test_remove_from_queue_invalid_id(manager):
    with pytest.raises(RuntimeError):
        manager.remove_from_queue(999)


def test_current_tasks(manager):
    manager._current_tasks = {1: 1, 2: 2}
    tasks = manager.current_tasks()
    assert tasks == [1, 2]
