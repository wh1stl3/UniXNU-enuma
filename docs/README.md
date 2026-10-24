# README

热状态重跑曾成功的 geometry20-control 自动返回，已排除"人工恢复后残留状态"；同一条 step20/query1 今日 3 成功 1 超时。超时转为偶发出口嫌疑（ResetCold/PSCI 出口失效 vs SimpleFb MMIO 读挂死），断电冷启动不再执行。下一步做无显示 MMIO、无等待的早期停止点候选并重复多笔。见 STATUS，R-005 consumed。
