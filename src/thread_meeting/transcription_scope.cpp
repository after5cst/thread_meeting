#include "transcription_scope.h"
#include "globals.h"

TranscriptionScope::pointer_t TranscriptionScope::set_target()
{
    if (g_transcription)
    {
        // Someone else is already transcribing.  We can't get it.
        return nullptr;
    }
    auto target = std::make_shared<PeekableQueue>();
    g_transcription = target;
    return target;
}

void TranscriptionScope::clear_target(pointer_t& target)
{
    if (target)
    {
        g_transcription.reset();
    }
}
