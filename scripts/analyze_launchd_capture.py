#!/usr/bin/env python3
"""Conservative, order-based analysis of captured launchd service lines."""
import argparse
import re
from collections import defaultdict
from pathlib import Path

STAMP = re.compile(r"^\s*\[\s*(\d+(?:\.\d+)?)\]")
FRAME = re.compile(r"^\s*(\d+)\s*/\s*(\d+(?:\.\d+)?)\s*/\s*(.*)$")
SERVICE = re.compile(
    r"(?:\((?:system|user/\d+|gui/\d+|pid/\d+)\s*/\s*)?"
    r"(?P<name>[A-Za-z_][\w.-]*)\s*\[(?P<pid>\d+)\]"
)
PID_FIRST = re.compile(r"\bpid/(?P<pid>\d+)\s+\[(?P<name>[A-Za-z_][\w.-]*)\]")
SPAWN = re.compile(r"Successfully spawned|state:\s*running|SOURCE_ATTACH", re.I)
EXIT = re.compile(r"\bexited\b", re.I)
LAUNCHD = re.compile(r"\blaunchd(?:\[1\])?\b", re.I)


def analyze(text, mode, complete=False):
    services = defaultdict(list)
    exits, unmatched, backwards, events = [], [], [], []
    previous_stamp = None
    last_frame = -1
    for number, line in enumerate(text.splitlines(), 1):
        loc = f"L{number}"
        if mode == "frames":
            match = FRAME.match(line)
            if not match:
                if line.strip():
                    raise ValueError(f"L{number}: expected frame/real-seconds/new-line")
                continue
            frame = int(match.group(1))
            if frame < last_frame:
                raise ValueError(f"L{number}: frame numbers decrease")
            last_frame = frame
            loc += f" frame={frame} real={match.group(2)}s"
            line = match.group(3)
        stamp = STAMP.match(line)
        if stamp:
            value = float(stamp.group(1))
            if previous_stamp and value < previous_stamp[0]:
                backwards.append(f"{previous_stamp[1]} {previous_stamp[0]:g} -> {loc} {value:g}")
            previous_stamp = value, loc
            loc += f" timestamp={stamp.group(1)}"
        # Require an actual launchd log envelope, not prose about observations.
        if not LAUNCHD.search(line):
            continue
        matches = [m for m in SERVICE.finditer(line) if m.group("name").lower() != "launchd"]
        matches += list(PID_FIRST.finditer(line))
        if EXIT.search(line):
            if len(matches) == 1:
                m = matches[0]
                exits.append((m.group("name"), int(m.group("pid")), loc))
            else:
                unmatched.append(loc + " " + line.strip())
        for m in matches:
            name, pid = m.group("name"), int(m.group("pid"))
            services[name].append((pid, loc))
            if SPAWN.search(line) and not EXIT.search(line):
                events.append((name, pid, loc, number))
    lines = ["服务出现次数与 pid 序列（按匹配行）:"]
    for name, occurrences in sorted(services.items()):
        lines.append(f"  {name}: {len(occurrences)} 次; pid " +
                     ", ".join(f"{pid}@{loc}" for pid, loc in occurrences))
    if not services:
        lines.append("  无可识别服务行")
    lines.append("exited:")
    for name, pid, loc in exits:
        lines.append(f"  {loc}: {name}[{pid}]")
    for item in unmatched:
        lines.append(f"  未能唯一关联: {item}")
    if not exits and not unmatched:
        lines.append("  无")
    lines.append("递增新 pid:")
    chains = defaultdict(list)
    for name, occurrences in sorted(services.items()):
        previous = None
        for pid, loc in occurrences:
            if previous and pid > previous[0]:
                lines.append(f"  {name}: {previous[0]}@{previous[1]} -> {pid}@{loc}")
            previous = (pid, loc)
    # Deduplicate repeated state lines for the same process.
    seen = set()
    unique_events = []
    for event in events:
        key = event[:2]
        if key not in seen:
            seen.add(key)
            unique_events.append(event)
            chains[event[0]].append(event)
    respawn = []
    for name, chain in chains.items():
        for a, b, c in zip(chain, chain[1:], chain[2:]):
            if a[1] < b[1] < c[1]:
                exit_rows = [(p, int(re.match(r"L(\d+)", loc).group(1)))
                             for n, p, loc in exits if n == name]
                if (any(p == a[1] and a[3] < row < b[3] for p, row in exit_rows)
                        and any(p == b[1] and b[3] < row < c[3] for p, row in exit_rows)):
                    respawn.append(name)
    if not any(any(b[0] > a[0] for a, b in zip(v, v[1:])) for v in services.values()):
        lines.append("  无")
    lines.append("连续新服务段（识别到的启动事件）:")
    segments, segment, seen_names = [], [], set()
    for event in unique_events:
        if event[0] in seen_names:
            if segment:
                segments.append(segment)
            segment = []
        else:
            segment.append(event)
            seen_names.add(event[0])
    if segment:
        segments.append(segment)
    for segment in segments:
        if len(segment) >= 2:
            lines.append("  " + " -> ".join(f"{n}[{p}]@{loc}" for n, p, loc, _ in segment))
    if not any(len(s) >= 2 for s in segments):
        lines.append("  无")
    lines.append("时间戳倒退:")
    lines.extend("  " + item for item in backwards)
    if not backwards:
        lines.append("  未发现（不代表时钟可靠）")
    if respawn:
        conclusion = "respawn 环（观察到同一服务两次退出后以递增 pid 重启: " + ", ".join(sorted(set(respawn))) + "）"
    elif complete and len(seen_names) >= 3 and not unmatched and not exits:
        conclusion = "推进（仅限所捕获窗口；至少三个新服务启动，未见退出）"
    else:
        conclusion = "无法判定（缺连续完整捕获及可关联服务名/pid 的启动、退出序列；不得将日志缺失视为未退出）"
    lines.append("结论: " + conclusion)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=("serial", "frames"), required=True)
    parser.add_argument("--complete", action="store_true",
                        help="operator attests full, ordered capture without gaps")
    args = parser.parse_args()
    try:
        print(analyze(args.input.read_text(encoding="utf-8"), args.format, args.complete))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
