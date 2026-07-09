"""解析 pytest junitxml，按「端 / 测试文件」聚合统计。

用法：python tools/parse_junit.py reports/junit_full.xml
"""
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict


def main(path: str) -> None:
    root = ET.parse(path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")

    by_end = defaultdict(lambda: [0, 0, 0, 0])   # total, fail, err, skip
    by_file = defaultdict(lambda: [0, 0, 0, 0])

    for tc in suite.iter("testcase"):
        cls = tc.get("classname", "")
        parts = cls.split(".")
        end = parts[1] if len(parts) > 1 and parts[0] == "tests" else parts[0]
        fname = ".".join(parts[:3]) if len(parts) >= 3 else cls
        kids = [c.tag for c in tc]
        fail = 1 if "failure" in kids else 0
        err = 1 if "error" in kids else 0
        skip = 1 if "skipped" in kids else 0
        for d in (by_end[end], by_file[fname]):
            d[0] += 1
            d[1] += fail
            d[2] += err
            d[3] += skip

    print("=== 按端汇总 (total / fail / err / skip / pass) ===")
    g = [0, 0, 0, 0]
    for k in sorted(by_end):
        d = by_end[k]
        p = d[0] - d[1] - d[2] - d[3]
        for i in range(4):
            g[i] += d[i]
        print("{:14} total={:4} fail={} err={} skip={} pass={}".format(
            k, d[0], d[1], d[2], d[3], p))
    gp = g[0] - g[1] - g[2] - g[3]
    print("{:14} total={:4} fail={} err={} skip={} pass={}".format(
        "TOTAL", g[0], g[1], g[2], g[3], gp))

    print("\n=== 按测试文件 ===")
    for k in sorted(by_file):
        d = by_file[k]
        p = d[0] - d[1] - d[2] - d[3]
        flag = "" if (d[1] + d[2]) == 0 else "  <== 有失败/错误"
        print("{:58} total={:3} fail={} err={} skip={} pass={}{}".format(
            k, d[0], d[1], d[2], d[3], p, flag))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "reports/junit_full.xml")
