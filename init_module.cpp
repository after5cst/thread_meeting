#include "src/thread_meeting/attendee.h"
#include "src/thread_meeting/baton.h"
#include "src/thread_meeting/enter_exit.h"
#include "src/thread_meeting/functions.h"
#include "src/thread_meeting/keep.h"
#include "src/thread_meeting/peekable_queue.h"
#include "src/thread_meeting/take.h"
#include "src/thread_meeting/transcript_item.h"

//#include "attendee_scope.h"
//#include "baton_scope.h"

PYBIND11_MODULE(thread_meeting, m) {
  m.doc() = R"pbdoc(
        thread_meeting plugin
        **************************

        .. currentmodule:: thread_meeting

        .. autosummary::
           :toctree: _generate

           Attendee
           Baton
           Keep
           PeekableQueue
           Take
           TakeStatus
           TranscriptItem
           TranscriptType
           _EnterExit

           me
           participate
           starting_baton
           transcribe
           transcriber

    )pbdoc";

  bind_functions(m);
  Attendee::bind(m);
  Baton::bind(m);
  EnterExit::bind(m);
  Keep::bind(m);
  Take::bind(m);
  TranscriptItem::bind(m);
  PeekableQueue::bind(m);

  // If the initial thread ID (presumably main) hasn't been set,
  // then set it to whatever we have right now.  If you import
  // this module from a worker thread first, it may be wrong.
  if (0 == g_initial_thread_id) {
    g_initial_thread_id = PyThread_get_thread_ident();
  }

#ifdef VERSION_INFO
  m.attr("__version__") = VERSION_INFO;
#else
  m.attr("__version__") = "dev";
#endif
}
