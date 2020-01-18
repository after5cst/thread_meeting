#include "transcription_scope.h"

#include "globals.h"
#include "transcription_item.h"

TranscriptionScope::pointer_t TranscriptionScope::set_target()
{

    auto &transcript = g_transcripts[thread_id()];
    if (transcript)
    {
        // This thread already has a transcript.  Since I define a transcript
        // as global to the thread, an attempt to create a second one will
        // fail.  By design, although this could be up for review.
        return nullptr;
    }

    auto target = std::make_shared<PeekableQueue>();
    transcript = target;

    // Normally, you should use the global function transcribe() to add 
    // transcription items.  But in this special case, we only want to 
    // transcribe the fact that the transcript has started to the 
    // transcript that started (the others don't care).
    auto item = pybind11::cast(TranscriptionItem("Transcript started", 
        TranscriptionType::enter));

    transcript->append(item);

    return target;
}

void TranscriptionScope::clear_target(pointer_t& target)
{
    if (target)
    {
        // See set_target() for explanation why transcribe() is not used.
        auto item = pybind11::cast(TranscriptionItem("Transcript ended", 
            TranscriptionType::exit));
        target->append(item);
        g_transcripts.erase(thread_id());
        target.reset();
    }
}
