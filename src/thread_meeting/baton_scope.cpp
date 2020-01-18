#include "baton_scope.h"

#include "baton.h"
#include "globals.h"

BatonScope::pointer_t BatonScope::set_target()
{
    if ((!m_valid) || g_baton.lock())
    {
        // Someone else has the baton.  We can't get it.
        return nullptr;
    }
    auto target = std::make_shared<Baton>();
    g_baton = target;

    transcribe("Baton", TranscriptType::enter);

    return target;
}

void BatonScope::clear_target(pointer_t& target)
{
    if (target)
    {
        transcribe("Baton", TranscriptType::exit);
        g_baton.reset();
        target->invalidate();
        target.reset();
    }
}
