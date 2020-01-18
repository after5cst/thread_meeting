#include "attendee.h"
#include "baton.h"
#include "enter_exit.h"
#include "functions.h"
#include "keep.h"
#include "take.h"
#include "peekable_queue.h"
#include "transcription_item.h"

//#include "attendee_scope.h"
//#include "baton_scope.h"

PYBIND11_MODULE(thread_meeting, m) {
    m.doc() = R"pbdoc(
        thread_meeting plugin
        -----------------------

        .. currentmodule:: thread_meeting

        .. autosummary::
           :toctree: _generate

           attend
           Attendee
           Keep
           Take
    )pbdoc";

    bind_functions(m);
    Attendee::bind(m);
    Baton::bind(m);
    EnterExit::bind(m);
    Keep::bind(m);
    Take::bind(m);
    TranscriptionItem::bind(m);
    PeekableQueue::bind(m);

    // If the initial thread ID (presumably main) hasn't been set,
    // then set it to whatever we have right now.  If you import
    // this module from a worker thread first, it may be wrong.
    if (0 == g_initial_thread_id)
    {
        g_initial_thread_id = PyThread_get_thread_ident();
    }

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
