// SPDX-License-Identifier: MIT
// From HuajiFruit/UniXNU-sirius@ac0c900485f3c0cd18de9707579a1cdcd3365503,
// package/BootWatchdogPolicy.c. Only the watchdogd and lite=1 paths are used.
// Called once, after scratch Data mounts and before PID 1 execs launchd.
#include <sys/param.h>
#include <sys/systm.h>
#include <sys/proc.h>
#include <sys/sysproto.h>
#include <sys/fcntl.h>
#include <sys/stat.h>
#include <pexpert/pexpert.h>

static const char policy_head[] =
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
    "<plist version=\"1.0\"><dict>";
static const char policy_watchdogd[] = "<key>com.apple.watchdogd</key><true/>";
static const char policy_tail[] = "</dict></plist>\n";
static const char lite_jobs[] =
    "com.apple.identityservicesd,com.apple.locationd,com.apple.CommCenter,com.apple.bluetoothd";
static char policy[2048];

static int
append_job(const char **cursor)
{
    const char *label = *cursor;
    const char *end = label;
    while (*end && *end != ',') {
        ++end;
    }
    if (strlcat(policy, "<key>", sizeof(policy)) >= sizeof(policy)) {
        return EINVAL;
    }
    size_t at = strlen(policy), len = (size_t)(end - label);
    if (at + len >= sizeof(policy)) {
        return EINVAL;
    }
    memcpy(policy + at, label, len);
    policy[at + len] = '\0';
    *cursor = *end ? end + 1 : end;
    return strlcat(policy, "</key><true/>", sizeof(policy)) >= sizeof(policy) ? EINVAL : 0;
}

int sheng_boot_watchdog_policy(void *, uint64_t);

int
sheng_boot_watchdog_policy(void *process, uint64_t scratch)
{
    proc_t p = process;
    int watchdog = 0, lite = 0, error, fd = -1;
    int32_t result = 0;
    PE_parse_boot_argn("sheng-disable-watchdogd", &watchdog, sizeof(watchdog));
    PE_parse_boot_argn("sheng-lite", &lite, sizeof(lite));
    if (watchdog != 1 && lite != 1) {
        return 0;
    }

    strlcpy(policy, policy_head, sizeof(policy));
    if (watchdog == 1) {
        strlcat(policy, policy_watchdogd, sizeof(policy));
    }
    if (lite == 1) {
        for (const char *job = lite_jobs; *job;) {
            if ((error = append_job(&job))) {
                return error;
            }
        }
    }
    if (strlcat(policy, policy_tail, sizeof(policy)) >= sizeof(policy)) {
        return EINVAL;
    }
    static const char directory[] = "/private/var/db/com.apple.xpc.launchd";
    static const char path[] = "/private/var/db/com.apple.xpc.launchd/disabled.plist";
    if ((error = copyout(directory, scratch, sizeof(directory)))) {
        goto done;
    }
    struct mkdir_args md = {.path = scratch, .mode = 0755};
    error = mkdir(p, &md, &result);
    if (error && error != EEXIST) {
        goto done;
    }
    if ((error = copyout(path, scratch, sizeof(path)))) {
        goto done;
    }
    struct open_args op = {.path = scratch, .flags = O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW, .mode = 0644};
    if ((error = open(p, &op, &result))) {
        goto done;
    }
    fd = result;
    // Keep the pre-existing SystemOS exec environment at +0x400 and above intact.
    for (size_t sent = 0, total = strlen(policy); sent < total;) {
        size_t piece = MIN(total - sent, (size_t)0x1f0);
        if ((error = copyout(policy + sent, scratch + 0x200, piece))) {
            goto done;
        }
        struct write_args wr = {.fd = fd, .cbuf = scratch + 0x200, .nbyte = piece};
        user_ssize_t written = 0;
        if ((error = write(p, &wr, &written))) {
            goto done;
        }
        if (written != (user_ssize_t)piece) {
            error = EIO;
            goto done;
        }
        sent += piece;
    }
    struct fchown_args owner = {.fd = fd, .uid = 0, .gid = 0};
    struct fchmod_args mode = {.fd = fd, .mode = 0644};
    struct fsync_args sync = {.fd = fd};
    struct fstat64_args sa = {.fd = fd, .ub = scratch + 0x800};
    struct stat64 st = {0};
    if ((error = fchown(p, &owner, &result)) ||
        (error = fchmod(p, &mode, &result)) ||
        (error = fsync(p, &sync, &result)) ||
        (error = sys_fstat64(p, &sa, &result)) ||
        (error = copyin(sa.ub, &st, sizeof(st)))) {
        goto done;
    }
    if (st.st_uid != 0 || st.st_gid != 0 || !S_ISREG(st.st_mode) ||
        (st.st_mode & 0777) != 0644 || st.st_size != (off_t)strlen(policy)) {
        error = EINVAL;
    }
done:
    if (fd >= 0) {
        struct close_args cl = {.fd = fd};
        int close_error = sys_close(p, &cl, &result);
        if (!error) {
            error = close_error;
        }
    }
    if (!error) {
        static const char marker[] = "/private/var/db/com.apple.xpc.launchd/disabled.migrated";
        error = copyout(marker, scratch, sizeof(marker));
        if (!error) {
            struct open_args mark = {.path = scratch, .flags = O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, .mode = 0644};
            error = open(p, &mark, &result);
            if (!error) {
                struct close_args cl = {.fd = result};
                error = sys_close(p, &cl, &result);
            } else if (error == EEXIST) {
                error = 0;
            }
        }
    }
    printf("enuma launch policy: watchdogd=%d lite=%d errno=%d\n", watchdog == 1, lite == 1, error);
    return error;
}
