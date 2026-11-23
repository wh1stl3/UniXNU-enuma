/* SPDX-License-Identifier: BSD-2-Clause-Patent */
/* BSD lookup bridge: invoked only from the OSFMK snapshot worker. */
extern thread_call_t enuma_th_alloc(unsigned int tick);
task_t enuma_th_task_ref(int pid, const char *comm, const char **why);

task_t
enuma_th_task_ref(int pid, const char *comm, const char **why)
{
	proc_t proc = proc_find(pid);
	if (proc == PROC_NULL) {
		*why = "missing";
		return TASK_NULL;
	}
	if (strncmp(proc->p_comm, comm, sizeof(proc->p_comm)) != 0) {
		proc_rele(proc);
		*why = "comm";
		return TASK_NULL;
	}
	task_t task = proc_task(proc);
	if (task != TASK_NULL) {
		task_reference(task);
	} else {
		*why = "no-task";
	}
	proc_rele(proc);
	return task;
}
