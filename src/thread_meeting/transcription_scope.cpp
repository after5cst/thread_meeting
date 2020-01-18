#include "transcription_scope.h"

#include "globals.h"

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

    transcribe("Transcription started", TranscriptionType::enter);
    return target;
}

void TranscriptionScope::clear_target(pointer_t& target)
{
    if (target)
    {
        transcribe("Transcription ended", TranscriptionType::exit);
        g_transcripts.erase(thread_id());
    }
}
