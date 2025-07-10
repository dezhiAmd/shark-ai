# Copyright 2024 Advanced Micro Devices, Inc.
#
# Licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from shortfin_apps.utils import SystemManager
import os


class LlmSystemManager(SystemManager):
    def __init__(
        self,
        device: str = "local-task",
        device_ids: list = None,
        async_allocs: bool = True,
        async_caching: bool = True,
        amdgpu_allocators: list = None,
        amdgpu_allow_device_reuse: bool = False,
        stream_num: int = 1,
    ):
        os.environ['SHORTFIN_AMDGPU_LOGICAL_DEVICES_PER_PHYSICAL_DEVICE'] = str(stream_num)
        super().__init__(
            device=device,
            device_ids=device_ids,
            async_allocs=async_allocs,
            async_caching=async_caching,
            amdgpu_allocators=amdgpu_allocators,
            amdgpu_allow_device_reuse=amdgpu_allow_device_reuse,
            logger_name=__name__,
            shutdown_system=False,
        )
        self.stream_num = stream_num
