#include "transcript_scope.h"

#include "globals.h"
#include "transcript_item.h"

TranscriptScope::pointer_t TranscriptScope::set_target() {

  auto &transcript = g_transcripts[thread_id()];
  if (transcript) {
    // This thread already has a transcript.  Since I define a transcript
    // as global to the thread, an attempt to create a second one will
    // fail.  By design, although this could be up for review.
    return nullptr;
  }

  auto target = std::make_shared<PriorityQueue>();
  transcript = target;

  // Normally, you should use the global function transcribe() to add
  // transcript items.  But in this special case, we only want to
  // transcribe the fact that the transcript has started to the
  // transcript that started (the others don't care).
  auto item =
      pybind11::cast(TranscriptItem("Transcript", TranscriptType::enter));

  transcript->push_low(item);

  return target;
}

void TranscriptScope::clear_target(pointer_t &target) {
  if (target) {
    // See set_target() for explanation why transcribe() is not used.
    auto item =
        pybind11::cast(TranscriptItem("Transcript", TranscriptType::exit));
    target->push_low(item);
    g_transcripts.erase(thread_id());
    target.reset();
  }
}
