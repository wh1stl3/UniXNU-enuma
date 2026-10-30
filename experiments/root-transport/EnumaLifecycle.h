// SPDX-License-Identifier: BSD-2-Clause-Patent
#pragma once
// Ops lock/unlock serialize state only; read and quiesce run outside it.
// Caller retains service, Ops, request buffers and DMA lifetime throughout.
// requestStop is nonblocking and can be called from a completion callback.
// tryDrain must be called by the owner after pending readers finish. It never
// cancels hardware or frees resources. Failed/quarantined objects are retained.
enum class EnumaLife { Cold, Online, Draining, Quiescing, Stopped, Quarantined };
template<class Ops> class EnumaLifecycle {
    Ops &ops;
    EnumaLife phase=EnumaLife::Cold;
    unsigned active=0;
    struct Guard {
        Ops &ops;
        explicit Guard(Ops &o):ops(o){ops.lock();}
        ~Guard(){ops.unlock();}
    };
public:
    explicit EnumaLifecycle(Ops &o):ops(o){}
    EnumaLifecycle(const EnumaLifecycle &)=delete;
    EnumaLifecycle &operator=(const EnumaLifecycle &)=delete;
    // Owner calls only after takeover and all publication prerequisites.
    bool activate(bool qualified) {
        Guard guard(ops);
        if(phase!=EnumaLife::Cold || !qualified)return false;
        phase=EnumaLife::Online;return true;
    }
    // Read returns a result carrying status/done; completion stays with caller,
    // after this function returns and all internal locks have been released.
    template<class Request> auto read(const Request &request)->decltype(ops.read(request)) {
        {
            Guard guard(ops);
            if(phase!=EnumaLife::Online || active==~0U)return ops.rejected();
            ++active;
        }
        // Ops must not throw, and serializes actual transport/bounce access.
        auto result=ops.read(request);
        // A platform poison query may take its transport lock. Do not call
        // it under the state lock: a transport callback can requestStop().
        bool poisoned=ops.poisoned();
        {
            Guard guard(ops);
            --active;
            if(poisoned)phase=EnumaLife::Quarantined;
        }
        return result;
    }
    void requestStop() {
        Guard guard(ops);
        if(phase==EnumaLife::Online || phase==EnumaLife::Cold)phase=EnumaLife::Draining;
    }
    bool tryDrain() {
        {
            Guard guard(ops);
            if(phase==EnumaLife::Stopped)return true;
            if(phase!=EnumaLife::Draining || active)return false;
            phase=EnumaLife::Quiescing;
        }
        // Must prove BOTH queues and DMA stopped; false retains everything.
        bool quiet=ops.quiesce();
        Guard guard(ops);
        phase=quiet?EnumaLife::Stopped:EnumaLife::Quarantined;
        return quiet;
    }
    bool releasable() {Guard guard(ops);return phase==EnumaLife::Stopped && !active;}
};
