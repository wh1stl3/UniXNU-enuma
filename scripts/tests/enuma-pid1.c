/* SPDX-License-Identifier: BSD-2-Clause */
#define _XOPEN_SOURCE 700
#define ENUMA_PID1_HOST_TEST 1
#include <assert.h>
#include <limits.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>
#include "enuma_pid1.h"

enum { PRODUCERS = 12, EVENTS = 10000, ESnormal = 0 };
static struct ep_state state;
static pthread_barrier_t producers;
static void *produce(void *arg)
{
	uintptr_t n = (uintptr_t)arg;
	pthread_barrier_wait(&producers);
	for (int i = 0; i < EVENTS; i++) {
		ep_svc(&state, 1, UINT64_MAX, -(int32_t)n, n * 4096);
		ep_svc(&state, 1, 9, 42, 0); /* PID reuse cannot match */
		ep_svc(&state, 2, UINT64_MAX, 42, 0);
	}
	ep_exit_commit(&state, 1, UINT64_MAX, -(int32_t)n, 1, (uint32_t)n,
	    UINT64_C(0xfedcba9800000000) + n);
	return NULL;
}

static void test_publication(void)
{
	assert(!ep_begin(&state, 2, 1));
	assert(ep_begin(&state, 1, UINT64_MAX));
	assert(!ep_begin(&state, 1, 2));
	pthread_t threads[PRODUCERS];
	pthread_barrier_init(&producers, NULL, PRODUCERS + 1);
	for (uintptr_t i = 1; i <= PRODUCERS; i++) {
		assert(!pthread_create(&threads[i - 1], NULL, produce, (void *)i));
	}
	pthread_barrier_wait(&producers);
	/* Acquire observes a fully published immutable tuple during live production. */
	while (__atomic_load_n(&state.first.phase, __ATOMIC_ACQUIRE) != EP_READY) {}
	struct ep_first first = state.first;
	assert(first.pid == 1 && first.uniqueid == UINT64_MAX);
	assert(first.trap <= -1 && first.trap >= -PRODUCERS);
	assert(first.pc == (uint64_t)-first.trap * 4096);
	for (int i = 0; i < PRODUCERS; i++) {
		pthread_join(threads[i], NULL);
	}
	assert(__atomic_load_n(&state.svc_count, __ATOMIC_RELAXED) == PRODUCERS * EVENTS);
	assert(!memcmp(&first, &state.first, sizeof(first)));
	assert(__atomic_load_n(&state.exit.phase, __ATOMIC_ACQUIRE) == EP_READY);
	struct ep_exit exited = state.exit;
	assert(exited.wait_status == -(int32_t)exited.reason_namespace);
	assert(exited.reason_code == UINT64_C(0xfedcba9800000000) + exited.reason_namespace);
	ep_exit_commit(&state, 1, UINT64_MAX, 99, 0, 0, 0);
	assert(!memcmp(&exited, &state.exit, sizeof(exited)));
	pthread_barrier_destroy(&producers);

	/* Deliberately stranded WRITING slots: calls must finish, without reading
	 * the unfinished payload or waiting for its writer. */
	struct ep_state pending = {0};
	assert(ep_begin(&pending, 1, 7));
	assert(ep_claim(&pending.first.phase));
	assert(ep_claim(&pending.exit.phase));
	for (int i = 0; i < EVENTS; i++) {
		ep_svc(&pending, 1, 7, INT32_MIN, UINT64_MAX);
		ep_exit_commit(&pending, 1, 7, INT32_MIN, 1, UINT32_MAX, UINT64_MAX);
	}
	assert(pending.first.phase == EP_WRITING && pending.exit.phase == EP_WRITING);
	assert(pending.svc_count == EVENTS && pending.first.pc == 0);
	struct ep_state identity_pending = {0};
	assert(ep_claim(&identity_pending.target.phase));
	assert(!ep_matches(&identity_pending, 1, 0));
	ep_svc(&identity_pending, 1, 0, 0, 0);
	assert(identity_pending.svc_count == 0);
}

/* Actual reader from the patch, with fake gc primitives and a real mutex. */
static struct ep_console_gate enuma_pid1_console;
static struct { unsigned int v_columns, v_rows; } vinfo = {100, 6};
static unsigned int gc_x = 99, gc_y = 5;
static int gc_hanging_cursor = 1, gc_vt100state = ESnormal, gc_enabled = 1;
static pthread_mutex_t console_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_barrier_t reader_entered, reader_release, transition_done;
static _Thread_local int locked, is_reader;
static atomic_int interleave, characters, transition_attempted;
static void test_lock(void)
{
	assert(!locked); /* recursive lock is a test failure */
	pthread_mutex_lock(&console_lock);
	locked = 1;
}
static void test_unlock(void)
{
	assert(locked);
	locked = 0;
	pthread_mutex_unlock(&console_lock);
	if (is_reader && atomic_exchange(&interleave, 0)) {
		/* Schedule the writer between real reader batches deterministically. */
		pthread_barrier_wait(&transition_done);
	}
}
#define VCPUTC_LOCK_LOCK() test_lock()
#define VCPUTC_LOCK_UNLOCK() test_unlock()
static void gc_hide_cursor(unsigned int x, unsigned int y)
{
	assert(locked && x < vinfo.v_columns && y < vinfo.v_rows);
}
static void gc_show_cursor(unsigned int x, unsigned int y)
{
	assert(locked && x < vinfo.v_columns && y < vinfo.v_rows);
}
static void gc_putchar(char c)
{
	assert(locked && c >= ' ' && c <= '~');
	assert(gc_x < 96 && gc_y < 4 && !gc_hanging_cursor); /* no wrapping/scrolling */
	if (atomic_fetch_add(&characters, 1) == 0 && atomic_load(&interleave)) {
		pthread_barrier_wait(&reader_entered);
		pthread_barrier_wait(&reader_release);
	}
	gc_x++;
}
#include "reader.inc"

/* Actual bootstrap helper: lock initialization and thread-failure behavior. */
typedef int *thread_t;
typedef int kern_return_t;
enum { KERN_SUCCESS = 0 };
static struct ep_state enuma_pid1_state;
static uint32_t enuma_pid1_lock_ready;
static int gc_initialized, start_result, starts, references_dropped, fake_thread;
static void enuma_pid1_observer(void *p, int r) { (void)p; (void)r; }
static int kernel_thread_start(void (*fn)(void *, int), void *arg, thread_t *out)
{
	assert(!locked && fn == enuma_pid1_observer && arg == NULL);
	starts++;
	*out = &fake_thread;
	return start_result;
}
static void thread_deallocate(thread_t t)
{
	assert(!locked && t == &fake_thread);
	references_dropped++;
}
#include "begin.inc"

static void test_bootstrap(void)
{
	gc_initialized = 0;
	enuma_pid1_begin(1, 123);
	assert(starts == 0 && enuma_pid1_state.target.phase == EP_READY && !locked);
	assert(__atomic_load_n(&enuma_pid1_state.observer_start, __ATOMIC_ACQUIRE) == EP_START_SKIPPED);
	memset(&enuma_pid1_state, 0, sizeof(enuma_pid1_state));
	enuma_pid1_lock_ready = 1;
	gc_initialized = 1;
	enuma_pid1_console = (struct ep_console_gate){.seen_mapping = 1, .eligible = 1};
	start_result = 5; /* failure must not prevent target publication or boot release */
	enuma_pid1_begin(1, 456);
	assert(starts == 1 && references_dropped == 0 && enuma_pid1_state.target.phase == EP_READY);
	assert(__atomic_load_n(&enuma_pid1_state.observer_start, __ATOMIC_ACQUIRE) == EP_START_FAILED);
	assert(enuma_pid1_state.observer_result == 5);
	enuma_pid1_begin(1, 456);
	assert(starts == 1); /* no retry */
	memset(&enuma_pid1_state, 0, sizeof(enuma_pid1_state));
	enuma_pid1_console = (struct ep_console_gate){.seen_mapping = 1, .eligible = 1};
	start_result = KERN_SUCCESS;
	enuma_pid1_begin(1, 789);
	assert(starts == 2 && references_dropped == 1 && !locked);
	assert(__atomic_load_n(&enuma_pid1_state.observer_start, __ATOMIC_ACQUIRE) == EP_START_RUNNING);
	assert(enuma_pid1_state.observer_result == KERN_SUCCESS);
}

static void *reader(void *unused)
{
	(void)unused;
	is_reader = 1;
	enuma_pid1_write(0, "P1 REFRESH=1 SVC=0");
	return NULL;
}
static void *transition(void *unused)
{
	(void)unused;
	atomic_store(&transition_attempted, 1);
	test_lock();
	assert(!ep_console_enter(&enuma_pid1_console, 0));
	assert(atomic_load(&characters) == 16); /* drained batch, not partial */
	ep_console_leave(&enuma_pid1_console, 0, 0);
	test_unlock();
	pthread_barrier_wait(&transition_done);
	return NULL;
}

static void test_console(void)
{
	struct ep_console_gate g = {0};
	/* Pre-init never starts; initial owned mapping becomes eligible only on leave. */
	assert(!ep_console_start(&g, 0, 1));
	int first = ep_console_enter(&g, 1);
	assert(first && !ep_console_start(&g, 1, 1));
	ep_console_leave(&g, first, 1);
	/* Permitted NULL TextMode -> Acquire before start does not revoke. */
	for (int i = 0; i < 2; i++) {
		assert(!ep_console_enter(&g, 0));
		ep_console_leave(&g, 0, 0);
	}
	assert(!ep_console_start(&g, 1, 0));
	assert(ep_console_start(&g, 1, 1));
	assert(!ep_console_start(&g, 1, 1));
	assert(ep_console_can_write(&g, 1));
	enuma_pid1_console = g;
	enuma_pid1_write(0, "P1");
	assert(atomic_load(&characters) == 96);
	assert(gc_x == 99 && gc_y == 5 && gc_hanging_cursor == 1);
	assert(!locked);
	gc_vt100state = 1;
	enuma_pid1_write(0, "SKIP PARTIAL ESCAPE");
	assert(atomic_load(&characters) == 96);
	gc_vt100state = ESnormal;
	gc_enabled = 0;
	enuma_pid1_write(0, "DISABLED");
	assert(atomic_load(&characters) == 96);
	gc_enabled = 1;

	atomic_store(&characters, 0);
	atomic_store(&interleave, 1);
	pthread_barrier_init(&reader_entered, NULL, 2);
	pthread_barrier_init(&reader_release, NULL, 2);
	pthread_barrier_init(&transition_done, NULL, 2);
	pthread_t r, w;
	assert(!pthread_create(&r, NULL, reader, NULL));
	pthread_barrier_wait(&reader_entered);
	assert(!pthread_create(&w, NULL, transition, NULL));
	while (!atomic_load(&transition_attempted)) {}
	assert(atomic_load(&characters) == 1); /* writer cannot revoke mid-reader */
	pthread_barrier_wait(&reader_release);
	pthread_join(r, NULL);
	pthread_join(w, NULL);
	assert(atomic_load(&characters) == 16);
	assert(!ep_console_can_write(&enuma_pid1_console, 1));
	ep_console_enter(&enuma_pid1_console, 1);
	ep_console_leave(&enuma_pid1_console, 0, 1);
	assert(!ep_console_start(&enuma_pid1_console, 1, 1)); /* never restore */
	enuma_pid1_write(0, "NO RESTORE");
	assert(atomic_load(&characters) == 16);
	pthread_barrier_destroy(&reader_entered);
	pthread_barrier_destroy(&reader_release);
	pthread_barrier_destroy(&transition_done);

	/* External first mapping and subsequent self/external mapping are all rejected. */
	struct ep_console_gate external = {0}, later = {0};
	first = ep_console_enter(&external, 1);
	ep_console_leave(&external, first, 0);
	assert(!ep_console_start(&external, 1, 1));
	first = ep_console_enter(&external, 1);
	ep_console_leave(&external, first, 1);
	assert(!ep_console_start(&external, 1, 1));
	first = ep_console_enter(&later, 1);
	ep_console_leave(&later, first, 1);
	first = ep_console_enter(&later, 1);
	ep_console_leave(&later, first, 1);
	assert(later.revoked && !ep_console_start(&later, 1, 1));
}

int main(void)
{
	test_publication();
	test_console();
	test_bootstrap();
	puts("PASS: multi-producer publication, pending nonblocking, one exit, actual reader drain/bounds, permanent revoke");
	return 0;
}
