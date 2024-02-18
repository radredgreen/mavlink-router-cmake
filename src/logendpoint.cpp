/*
 * This file is part of the MAVLink Router project
 *
 * Copyright (C) 2017  Intel Corporation. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#include "logendpoint.h"

#include <dirent.h>
#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#include <algorithm>
#include <map>
#include <memory>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#include <common/log.h>
#include <common/util.h>

#include "mainloop.h"

#define ALIVE_TIMEOUT 5
#define MAX_RETRIES   10

// clang-format off
const ConfFile::OptionsTable LogEndpoint::option_table[] = {
    {"Log",             false, ConfFile::parse_stdstring,           OPTIONS_TABLE_STRUCT_FIELD(LogOptions, logs_dir)},
    {"LogMode",         false, LogEndpoint::parse_log_mode,         OPTIONS_TABLE_STRUCT_FIELD(LogOptions, log_mode)},
    {"MavlinkDialect",  false, LogEndpoint::parse_mavlink_dialect,  OPTIONS_TABLE_STRUCT_FIELD(LogOptions, mavlink_dialect)},
    {"MinFreeSpace",    false, ConfFile::parse_ul,                  OPTIONS_TABLE_STRUCT_FIELD(LogOptions, min_free_space)},
    {"MaxLogFiles",     false, ConfFile::parse_ul,                  OPTIONS_TABLE_STRUCT_FIELD(LogOptions, max_log_files)},
    {"LogSystemId",     false, LogEndpoint::parse_fcu_id,           OPTIONS_TABLE_STRUCT_FIELD(LogOptions, fcu_id)},
    {"LogTelemetry",    false, ConfFile::parse_bool,                OPTIONS_TABLE_STRUCT_FIELD(LogOptions, log_telemetry)},
    {}
};
// clang-format on

LogEndpoint::LogEndpoint(std::string name, LogOptions conf)
    : Endpoint{ENDPOINT_TYPE_LOG, std::move(name)}
    , _config{conf}
{
}

void LogEndpoint::_send_msg(const mavlink_message_t *msg, int target_sysid)
{
}

void LogEndpoint::mark_unfinished_logs()
{
}

void LogEndpoint::_delete_old_logs()
{
}

uint32_t LogEndpoint::_get_prefix(DIR *dir)
{
}

DIR *LogEndpoint::_open_or_create_dir(const char *name)
{
}

int LogEndpoint::_get_file(const char *extension)
{
}

void LogEndpoint::stop()
{
}

bool LogEndpoint::start()
{
}

bool LogEndpoint::_alive_timeout()
{
}

bool LogEndpoint::_fsync()
{
}

void LogEndpoint::_remove_logging_start_timeout()
{
}

bool LogEndpoint::_start_alive_timeout()
{
}

void LogEndpoint::_handle_auto_start_stop(const struct buffer *pbuf)
{
}

int LogEndpoint::parse_mavlink_dialect(const char *val, size_t val_len, void *storage,
                                       size_t storage_len)
{
}

#define MAX_LOG_MODE_SIZE 20
int LogEndpoint::parse_log_mode(const char *val, size_t val_len, void *storage, size_t storage_len)
{
}
#undef MAX_LOG_MODE_SIZE

int LogEndpoint::parse_fcu_id(const char *val, size_t val_len, void *storage, size_t storage_len)
{
}
