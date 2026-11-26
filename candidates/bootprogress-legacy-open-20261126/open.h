/* SPDX-License-Identifier: BSD-2-Clause-Patent */
#ifndef ENUMA_LEGACY_OPEN_H
#define ENUMA_LEGACY_OPEN_H

enum enuma_open_phase { ENUMA_OPEN_NONE, ENUMA_OPEN_ATTEMPT, ENUMA_OPEN_RAW, ENUMA_OPEN_FINAL };
enum enuma_method_kind { ENUMA_METHOD_SYNC = 1, ENUMA_METHOD_VAR, ENUMA_METHOD_ASYNC };
enum enuma_chain_edge {
	ENUMA_DT_PARENT, ENUMA_DT_CHILD, ENUMA_FIRST_MATCH, ENUMA_ITER_SERVICE,
	ENUMA_OPEN_REJECT, ENUMA_OPEN_SERVICE, ENUMA_CHAIN_EDGES
};
enum enuma_open_reject { ENUMA_REJECT_MAC = 1, ENUMA_REJECT_PROPERTIES };

struct enuma_chain_point {
	bool seen, positive;
	uint32_t value;
	uint64_t key;
};

struct enuma_chain_snapshot {
	uint32_t generation;
	unsigned unsampled;
	bool available;
	struct enuma_chain_point point[ENUMA_CHAIN_EDGES];
};

struct enuma_open_snapshot {
	unsigned phase;
	struct { uint64_t uid; int pid, version; uint32_t generation, type; } attempt;
	struct { int result; bool truncated; char client_class[32]; } raw;
	struct { int err, result; bool client; } final;
	unsigned method_kind;
	uint32_t selector;
	bool method_eligible;
	struct enuma_chain_snapshot chain;
};

#ifdef __cplusplus
extern "C" {
#endif
bool enuma_legacy_open_claim(uint32_t, uint64_t);
void enuma_chain_note(unsigned, uint32_t, bool, uint64_t);
void enuma_legacy_open_raw(int, const char *);
void enuma_legacy_open_final(int, int, bool, uint64_t);
uint64_t enuma_legacy_method_key(void);
void enuma_legacy_method_note(uint32_t, unsigned);
void enuma_legacy_open_read(struct enuma_open_snapshot *);
#ifdef __cplusplus
}
#endif
#endif
