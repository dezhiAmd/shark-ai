// Copyright 2024 Advanced Micro Devices, Inc.
//
// Licensed under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

#include <cstdlib>
#include "shortfin/support/logging.h"

#include "spdlog/cfg/env.h"

bool SHORTFIN_SCHED_LOG_ENABLED=false;

namespace shortfin::logging {

void InitializeFromEnv() {
  const char* env = std::getenv("SHORTFIN_SCHED_LOG_ENABLED");
  SHORTFIN_SCHED_LOG_ENABLED = (env != nullptr && std::string(env) == "1");
  spdlog::cfg::load_env_levels();
}

}  // namespace shortfin::logging
