// SPDX-License-Identifier: BSD-2-Clause-Patent
#pragma once
#include "EnumaStorageOwner.h"
enum class EnumaSubmission { Accepted, BadArgument, NotWritable };
// Synchronous implementation of an asynchronous IOKit contract: rejection does
// not call completion; accepted requests complete exactly once, outside locks.
// Caller retains descriptor, service and completion context across this call.
inline EnumaSubmission enumaBlockSubmit(EnumaStorageOwner &owner, uint64_t sectors,
    uint64_t descriptorBytes, bool readOnlyDirection, const EnumaReadRequest &request,
    void *context, void (*complete)(void *, enuma_root_result)) {
    if (!complete || !request.destination || !request.copy || !request.count ||
        request.sector >= sectors || request.count > sectors-request.sector ||
        request.count > UINT64_MAX/512 || descriptorBytes < request.count*512)
        return EnumaSubmission::BadArgument;
    if (!readOnlyDirection) return EnumaSubmission::NotWritable;
    auto result=owner.read(request);
    complete(context,result);
    return EnumaSubmission::Accepted;
}
